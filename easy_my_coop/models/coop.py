# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

# pylint: disable=missing-manifest-dependency
from addons.base_iban.models.res_partner_bank import validate_iban

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

# This structure is only used in easy_my_coop_webstite's controller
_REQUIRED = [
    "email",
    "firstname",
    "lastname",
    "birthdate",
    "street_name",
    "house_number",
    "share_product_id",
    "ordered_parts",
    "zip_code",
    "city",
    "iban",
    "gender",
]


@api.model
def _lang_get(self):
    languages = self.env["res.lang"].search([])
    return [(language.code, language.name) for language in languages]


# todo move to subscription_request.py
class SubscriptionRequest(models.Model):
    _name = "subscription.request"
    _description = "Subscription Request"

    # This function is only used in easy_my_coop_webstite's controller
    def get_required_field(self):
        required_fields = _REQUIRED
        company = self.env["res.company"]._company_default_get()
        if company.data_policy_approval_required:
            required_fields.append("data_policy_approved")
        if company.internal_rules_approval_required:
            required_fields.append("internal_rules_approved")
        if company.financial_risk_approval_required:
            required_fields.append("financial_risk_approved")
        return required_fields

    def get_mail_template_notif(self, is_company=False):
        if is_company:
            mail_template = "easy_my_coop.email_template_confirmation_company"
        else:
            mail_template = "easy_my_coop.email_template_confirmation"
        return self.env.ref(mail_template, False)

    def is_member(self, vals, cooperator):
        if cooperator.member:
            vals["type"] = "increase"
            vals["already_cooperator"] = True
        return vals

    @api.model
    def create(self, vals):
        partner_obj = self.env["res.partner"]

        if not vals.get("partner_id"):
            cooperator = False
            if vals.get("email"):
                cooperator = partner_obj.get_cooperator_from_email(
                    vals.get("email")
                )
            if cooperator:
                vals["type"] = "subscription"
                vals = self.is_member(vals, cooperator)
                vals["partner_id"] = cooperator.id
        else:
            cooperator_id = vals.get("partner_id")
            cooperator = partner_obj.browse(cooperator_id)
            vals = self.is_member(vals, cooperator)

        if not cooperator.cooperator:
            cooperator.write({"cooperator": True})
        subscr_request = super(SubscriptionRequest, self).create(vals)

        if self._send_confirmation_email():
            mail_template_notif = subscr_request.get_mail_template_notif(is_company=False)
            mail_template_notif.send_mail(subscr_request.id)

        return subscr_request

    @api.model
    def create_comp_sub_req(self, vals):
        vals["name"] = vals["company_name"]
        if not vals.get("partner_id"):
            cooperator = self.env["res.partner"].get_cooperator_from_crn(
                vals.get("company_register_number")
            )
            if cooperator:
                vals["type"] = "subscription"
                vals = self.is_member(vals, cooperator)
                vals["partner_id"] = cooperator.id
        subscr_request = super(SubscriptionRequest, self).create(vals)

        if self._send_confirmation_email():
            confirmation_mail_template = subscr_request.get_mail_template_notif(
                is_company=True
            )
            confirmation_mail_template.send_mail(subscr_request.id)

        return subscr_request

    def check_empty_string(self, value):
        if value is None or value is False or value == "":
            return False
        return True

    def check_iban(self, iban):
        try:
            if iban:
                validate_iban(iban)
                return True
            else:
                return False
        except ValidationError:
            return False

    @api.multi
    @api.depends("iban", "skip_control_ng")
    def _compute_validated_lines(self):
        for sub_request in self:
            validated = sub_request.skip_control_ng or self.check_iban(
                sub_request.iban
            )
            sub_request.validated = validated

    @api.multi
    @api.depends(
        "share_product_id", "share_product_id.list_price", "ordered_parts"
    )
    def _compute_subscription_amount(self):
        for sub_request in self:
            sub_request.subscription_amount = (
                sub_request.share_product_id.list_price
                * sub_request.ordered_parts
            )

    already_cooperator = fields.Boolean(
        string="I'm already cooperator",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    name = fields.Char(
        string="Name",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    firstname = fields.Char(
        string="Firstname",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    lastname = fields.Char(
        string="Lastname",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    birthdate = fields.Date(
        string="Birthdate",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    gender = fields.Selection(
        [("male", _("Male")), ("female", _("Female")), ("other", _("Other"))],
        string="Gender",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    type = fields.Selection(
        [
            ("new", "New Cooperator"),
            ("subscription", "Subscription"),
            ("increase", "Increase number of share"),
        ],
        string="Type",
        default="new",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("block", "Blocked"),
            ("done", "Done"),
            ("waiting", "Waiting"),
            ("transfer", "Transfer"),
            ("cancelled", "Cancelled"),
            ("paid", "paid"),
        ],
        string="State",
        required=True,
        default="draft",
    )
    email = fields.Char(
        string="Email",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    iban = fields.Char(
        string="Account Number",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Cooperator",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    share_product_id = fields.Many2one(
        "product.product",
        string="Share type",
        domain=[("is_share", "=", True)],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    share_short_name = fields.Char(
        related="share_product_id.short_name",
        string="Share type name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    share_unit_price = fields.Float(
        related="share_product_id.list_price",
        string="Share price",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    subscription_amount = fields.Monetary(
        compute="_compute_subscription_amount",
        string="Subscription amount",
        currency_field="company_currency_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    ordered_parts = fields.Integer(
        string="Number of Share",
        required=True,
        readonly=True,
        default=1,
        states={"draft": [("readonly", False)]},
    )
    address = fields.Char(
        string="Address",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    city = fields.Char(
        string="City",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    zip_code = fields.Char(
        string="Zip Code",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        ondelete="restrict",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    phone = fields.Char(
        string="Phone", readonly=True, states={"draft": [("readonly", False)]}
    )
    user_id = fields.Many2one("res.users", string="Responsible", readonly=True)
    # todo rename to valid_subscription_request
    validated = fields.Boolean(
        compute="_compute_validated_lines",
        string="Valid Subscription request?",
        readonly=True,
    )
    skip_control_ng = fields.Boolean(
        string="Skip control",
        help="if this field is checked then no"
        " control will be done on the national"
        " register number and on the iban bank"
        " account. To be done in case of the id"
        " card is from abroad or in case of"
        " a passport",
    )
    lang = fields.Selection(
        _lang_get,
        string="Language",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env["res.company"]
        ._company_default_get()
        .default_lang_id.code,
    )
    date = fields.Date(
        string="Subscription date request",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: datetime.strftime(datetime.now(), "%Y-%m-%d"),
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    is_company = fields.Boolean(
        string="Is a company",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    is_operation = fields.Boolean(
        string="Is an operation",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_name = fields.Char(
        string="Company name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_email = fields.Char(
        string="Company email",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_register_number = fields.Char(
        string="Company register number",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_type = fields.Selection(
        [("", "")],
        string="Company type",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    same_address = fields.Boolean(
        string="Same address",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    activities_address = fields.Char(
        string="Activities address",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    activities_city = fields.Char(
        string="Activities city",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    activities_zip_code = fields.Char(
        string="Activities zip Code",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    activities_country_id = fields.Many2one(
        "res.country",
        string="Activities country",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    contact_person_function = fields.Char(
        string="Function",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    operation_request_id = fields.Many2one(
        "operation.request",
        string="Operation Request",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    capital_release_request = fields.One2many(
        "account.invoice",
        "subscription_request",
        string="Capital release request",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    capital_release_request_date = fields.Date(
        string="Force the capital " "release request date",
        help="Keep empty to use the " "current date",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    source = fields.Selection(
        [
            ("website", "Website"),
            ("crm", "CRM"),
            ("manual", "Manual"),
            ("operation", "Operation"),
        ],
        string="Source",
        default="website",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    data_policy_approved = fields.Boolean(
        string="Data Policy Approved", default=False
    )
    internal_rules_approved = fields.Boolean(
        string="Approved Internal Rules", default=False
    )
    financial_risk_approved = fields.Boolean(
        string="Financial Risk Approved", default=False
    )

    _order = "id desc"

    def get_person_info(self, partner):
        self.firstname = partner.firstname
        self.name = partner.name
        self.lastname = partner.lastname
        self.email = partner.email
        self.birthdate = partner.birthdate_date
        self.gender = partner.gender
        self.address = partner.street
        self.city = partner.city
        self.zip_code = partner.zip
        self.country_id = partner.country_id
        self.phone = partner.phone
        self.lang = partner.lang

    @api.onchange("partner_id")
    def onchange_partner(self):
        partner = self.partner_id
        if partner:
            self.is_company = partner.is_company
            self.already_cooperator = partner.member
            if partner.bank_ids:
                self.iban = partner.bank_ids[0].acc_number
            if partner.member:
                self.type = "increase"
            if partner.is_company:
                self.company_name = partner.name
                self.company_email = partner.email
                self.company_register_number = partner.company_register_number
                representative = partner.get_representative()
                self.get_person_info(representative)
                self.contact_person_function = representative.function
            else:
                self.get_person_info(partner)

    # declare this function in order to be overriden
    def get_eater_vals(self, partner, share_product_id):  # noqa
        return {}

    def _prepare_invoice_line(self, product, partner, qty):
        self.ensure_one()
        account = (
            product.property_account_income_id
            or product.categ_id.property_account_income_categ_id
        )
        if not account:
            raise UserError(
                _(
                    "Please define income account for this product:"
                    ' "%s" (id:%d) - or for its category: "%s".'
                )
                % (product.name, product.id, product.categ_id.name)
            )

        fpos = partner.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            "name": product.name,
            "account_id": account.id,
            "price_unit": product.lst_price,
            "quantity": qty,
            "uom_id": product.uom_id.id,
            "product_id": product.id or False,
        }
        return res

    def get_capital_release_mail_template(self):
        template = "easy_my_coop.email_template_release_capital"
        return self.env.ref(template, False)

    def send_capital_release_request(self, invoice):
        email_template = self.get_capital_release_mail_template()

        if self.company_id.send_capital_release_email:
            # we send the email with the capital release request in attachment
            # TODO remove sudo() and give necessary access right
            email_template.sudo().send_mail(invoice.id, True)
            invoice.sent = True

    def get_journal(self):
        return self.env.ref("easy_my_coop.subscription_journal")

    def get_accounting_account(self):
        account_obj = self.env["account.account"]
        if self.company_id.property_cooperator_account:
            account = self.company_id.property_cooperator_account
        else:
            accounts = account_obj.search([("code", "=", "416000")])
            if accounts:
                account = accounts[0]
            else:
                raise UserError(
                    _("You must set a cooperator account on you company.")
                )
        return account

    def get_invoice_vals(self, partner):
        return {
            "partner_id": partner.id,
            "journal_id": self.get_journal().id,
            "account_id": self.get_accounting_account().id,
            "type": "out_invoice",
            "release_capital_request": True,
            "subscription_request": self.id,
        }

    def create_invoice(self, partner):
        # creating invoice and invoice lines
        invoice_vals = self.get_invoice_vals(partner)
        if self.capital_release_request_date:
            invoice_vals["date_invoice"] = self.capital_release_request_date
        invoice = self.env["account.invoice"].create(invoice_vals)
        vals = self._prepare_invoice_line(
            self.share_product_id, partner, self.ordered_parts
        )
        vals["invoice_id"] = invoice.id
        self.env["account.invoice.line"].create(vals)

        # validate the capital release request
        invoice.action_invoice_open()

        self.send_capital_release_request(invoice)

        return invoice

    def get_partner_company_vals(self):
        partner_vals = {
            "name": self.company_name,
            "last_name": self.company_name,
            "is_company": self.is_company,
            "company_register_number": self.company_register_number,  # noqa
            "cooperator": True,
            "street": self.address,
            "zip": self.zip_code,
            "city": self.city,
            "email": self.company_email,
            "out_inv_comm_type": "bba",
            "customer": self.share_product_id.customer,
            "country_id": self.country_id.id,
            "lang": self.lang,
            "data_policy_approved": self.data_policy_approved,
            "internal_rules_approved": self.internal_rules_approved,
            "financial_risk_approved": self.financial_risk_approved,
        }
        return partner_vals

    def get_partner_vals(self):
        partner_vals = {
            "name": self.name,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "street": self.address,
            "zip": self.zip_code,
            "email": self.email,
            "gender": self.gender,
            "cooperator": True,
            "city": self.city,
            "phone": self.phone,
            "country_id": self.country_id.id,
            "lang": self.lang,
            "birthdate_date": self.birthdate,
            "customer": self.share_product_id.customer,
            "data_policy_approved": self.data_policy_approved,
            "internal_rules_approved": self.internal_rules_approved,
            "financial_risk_approved": self.financial_risk_approved,
        }
        return partner_vals

    def get_representative_vals(self):
        contact_vals = {
            "name": self.name,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "customer": False,
            "is_company": False,
            "cooperator": True,
            "street": self.address,
            "gender": self.gender,
            "zip": self.zip_code,
            "city": self.city,
            "phone": self.phone,
            "email": self.email,
            "country_id": self.country_id.id,
            "out_inv_comm_type": "bba",
            "out_inv_comm_algorithm": "random",
            "lang": self.lang,
            "birthdate_date": self.birthdate,
            "parent_id": self.partner_id.id,
            "representative": True,
            "function": self.contact_person_function,
            "type": "representative",
            "data_policy_approved": self.data_policy_approved,
            "internal_rules_approved": self.internal_rules_approved,
            "financial_risk_approved": self.financial_risk_approved,
        }
        return contact_vals

    def create_coop_partner(self):
        partner_obj = self.env["res.partner"]

        if self.is_company:
            partner_vals = self.get_partner_company_vals()
        else:
            partner_vals = self.get_partner_vals()

        partner = partner_obj.create(partner_vals)
        if self.iban:
            self.env["res.partner.bank"].create(
                {"partner_id": partner.id, "acc_number": self.iban}
            )
        return partner

    def set_membership(self):
        # To be overridden
        return True

    @api.multi
    def validate_subscription_request(self):
        self.ensure_one()
        # todo rename to validate (careful with iwp dependencies)
        partner_obj = self.env["res.partner"]

        if self.ordered_parts <= 0:
            raise UserError(_("Number of share must be greater than 0."))
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = None
            domain = []
            if self.already_cooperator:
                raise UserError(
                    _(
                        "The checkbox already cooperator is"
                        " checked please select a cooperator."
                    )
                )
            elif self.is_company and self.company_register_number:
                domain = [
                    (
                        "company_register_number",
                        "=",
                        self.company_register_number,
                    )
                ]  # noqa
            elif not self.is_company and self.email:
                domain = [("email", "=", self.email)]

            if domain:
                partner = partner_obj.search(domain)

        if not partner:
            partner = self.create_coop_partner()
            self.partner_id = partner
        else:
            partner = partner[0]

        partner.cooperator = True

        if self.is_company and not partner.has_representative():
            contact = False
            if self.email:
                domain = [("email", "=", self.email)]
                contact = partner_obj.search(domain)
                if contact:
                    contact.type = "representative"
            if not contact:
                contact_vals = self.get_representative_vals()
                partner_obj.create(contact_vals)
            else:
                if len(contact) > 1:
                    raise UserError(
                        _(
                            "There is two different persons with the"
                            " same national register number. Please"
                            " proceed to a merge before to continue"
                        )
                    )
                if contact.parent_id and contact.parent_id.id != partner.id:
                    raise UserError(
                        _(
                            "This contact person is already defined"
                            " for another company. Please select"
                            " another contact"
                        )
                    )
                else:
                    contact.write(
                        {"parent_id": partner.id, "representative": True}
                    )

        invoice = self.create_invoice(partner)
        self.write({"state": "done"})
        self.set_membership()

        return invoice

    @api.multi
    def block_subscription_request(self):
        self.ensure_one()
        self.write({"state": "block"})

    @api.multi
    def unblock_subscription_request(self):
        self.ensure_one()
        self.write({"state": "draft"})

    @api.multi
    def cancel_subscription_request(self):
        self.ensure_one()
        self.write({"state": "cancelled"})

    @api.multi
    def put_on_waiting_list(self):
        self.ensure_one()
        waiting_list_mail_template = self.env.ref(
            "easy_my_coop.email_template_waiting_list", False
        )
        waiting_list_mail_template.send_mail(self.id, True)
        self.write({"state": "waiting"})

    def _send_confirmation_email(self):
        return self.company_id.send_confirmation_email

# todo move to share_line.py
class ShareLine(models.Model):
    _name = "share.line"
    _description = "Share line"

    @api.multi
    def _compute_total_line(self):
        res = {}
        for line in self:
            line.total_amount_line = line.share_unit_price * line.share_number
        return res

    share_product_id = fields.Many2one(
        "product.product", string="Share type", required=True, readonly=True
    )
    share_number = fields.Integer(
        string="Number of Share", required=True, readonly=True
    )
    share_short_name = fields.Char(
        related="share_product_id.short_name",
        string="Share type name",
        readonly=True,
    )
    share_unit_price = fields.Monetary(
        string="Share price",
        currency_field="company_currency_id",
        readonly=True,
    )
    effective_date = fields.Date(string="Effective Date", readonly=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Cooperator",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    total_amount_line = fields.Monetary(
        string="Total amount line",
        currency_field="company_currency_id",
        compute="_compute_total_line",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
    )


# todo move to subscription_register.py
class SubscriptionRegister(models.Model):
    _name = "subscription.register"
    _description = "Subscription register"

    @api.multi
    def _compute_total_line(self):
        for line in self:
            line.total_amount_line = line.share_unit_price * line.quantity

    name = fields.Char(string="Number Operation", required=True, readonly=True)
    register_number_operation = fields.Integer(
        string="Register Number Operation", required=True, readonly=True
    )
    partner_id = fields.Many2one(
        "res.partner", string="Cooperator", required=True, readonly=True
    )
    partner_id_to = fields.Many2one(
        "res.partner", string="Transfered to", readonly=True
    )
    date = fields.Date(
        string="Subscription Date", required=True, readonly=True
    )
    quantity = fields.Integer(string="Number of share", readonly=True)
    share_unit_price = fields.Monetary(
        string="Share price",
        currency_field="company_currency_id",
        readonly=True,
    )
    total_amount_line = fields.Monetary(
        string="Total amount line",
        currency_field="company_currency_id",
        compute="_compute_total_line",
    )
    share_product_id = fields.Many2one(
        "product.product",
        string="Share type",
        required=True,
        readonly=True,
        domain=[("is_share", "=", True)],
    )
    share_short_name = fields.Char(
        related="share_product_id.short_name",
        string="Share type name",
        readonly=True,
    )
    share_to_product_id = fields.Many2one(
        "product.product",
        string="Share to type",
        readonly=True,
        domain=[("is_share", "=", True)],
    )
    share_to_short_name = fields.Char(
        related="share_to_product_id.short_name",
        string="Share to type name",
        readonly=True,
    )
    quantity_to = fields.Integer(string="Number of share to", readonly=True)
    share_to_unit_price = fields.Monetary(
        string="Share to price",
        currency_field="company_currency_id",
        readonly=True,
    )
    type = fields.Selection(
        [
            ("subscription", "Subscription"),
            ("transfer", "Transfer"),
            ("sell_back", "Sell Back"),
            ("convert", "Conversion"),
        ],
        string="Operation Type",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        readonly=True,
        default=lambda self: self.env.user,
    )

    _order = "register_number_operation asc"

    @api.model
    def read_group(
        self,
        domain,
        fields,
        groupby,
        offset=0,
        limit=None,
        orderby=False,
        lazy=True,
    ):
        if "share_unit_price" in fields:
            fields.remove("share_unit_price")
        if "register_number_operation" in fields:
            fields.remove("register_number_operation")
        res = super(SubscriptionRegister, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        if "total_amount_line" in fields:
            for line in res:
                if "__domain" in line:
                    lines = self.search(line["__domain"])
                    inv_value = 0.0
                    for line2 in lines:
                        inv_value += line2.total_amount_line
                    line["total_amount_line"] = inv_value
        return res
