# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_report_base_filename(self):
        self.ensure_one()
        if self.member:
            return "Cooperator Certificate - %s" % self.name
        else:
            return "unknown"

    @api.depends("share_ids")
    def _compute_effective_date(self):
        # TODO change it to compute it from the share register
        for partner in self:
            if partner.share_ids:
                partner.effective_date = partner.share_ids[0].effective_date
            else:
                partner.effective_date = False

    def _get_share_type(self):
        shares = self.env["product.product"].search([("is_share", "=", True)])
        share_types = [(s.default_code, s.short_name) for s in shares]
        return [("", "")] + share_types

    @api.depends(
        "share_ids",
        "share_ids.share_product_id",
        "share_ids.share_product_id.default_code",
        "share_ids.share_number",
    )
    def _compute_cooperator_type(self):
        for partner in self:
            share_type = ""
            for line in partner.share_ids:
                if line.share_number > 0:
                    share_type = line.share_product_id.default_code
                    break
            partner.cooperator_type = share_type

    @api.depends("share_ids")
    def _compute_share_info(self):
        for partner in self:
            number_of_share = 0
            total_value = 0.0
            for line in partner.share_ids:
                number_of_share += line.share_number
                total_value += line.share_unit_price * line.share_number
            partner.number_of_share = number_of_share
            partner.total_value = total_value

    cooperator = fields.Boolean(
        string="Cooperator",
        help="Check this box if this contact is a cooperator (effective or not).",
        copy=False,
    )
    member = fields.Boolean(
        string="Effective cooperator",
        help="Check this box if this cooperator is an effective member.",
        readonly=True,
        copy=False,
    )
    coop_candidate = fields.Boolean(
        string="Cooperator candidate",
        compute="_compute_coop_candidate",
        store=True,
        readonly=True,
    )
    old_member = fields.Boolean(
        string="Old cooperator",
        help="Check this box if this cooperator is no more an effective member.",
    )
    share_ids = fields.One2many("share.line", "partner_id", string="Share Lines")
    cooperator_register_number = fields.Integer(string="Cooperator Number", copy=False)
    number_of_share = fields.Integer(
        compute="_compute_share_info",
        string="Number of share",
        readonly=True,
    )
    total_value = fields.Float(
        compute="_compute_share_info",
        string="Total value of shares",
        readonly=True,
    )
    company_register_number = fields.Char(string="Company Register Number")
    cooperator_type = fields.Selection(
        selection="_get_share_type",
        compute=_compute_cooperator_type,
        string="Cooperator Type",
        store=True,
    )
    effective_date = fields.Date(
        string="Effective Date", compute=_compute_effective_date, store=True
    )
    representative = fields.Boolean(string="Legal Representative")
    representative_of_member_company = fields.Boolean(
        string="Legal Representative of Member Company",
        store=True,
        compute="_compute_representative_of_member_company",
    )
    # allows for representative to have their own address
    # see https://github.com/coopiteasy/vertical-cooperative/issues/350
    type = fields.Selection(selection_add=[("representative", "Representative")])
    subscription_request_ids = fields.One2many(
        "subscription.request", "partner_id", string="Subscription request"
    )
    legal_form = fields.Selection([], string="Legal form")
    data_policy_approved = fields.Boolean(string="Approved Data Policy")
    internal_rules_approved = fields.Boolean(string="Approved Internal Rules")
    financial_risk_approved = fields.Boolean(string="Approved Financial Risk")
    generic_rules_approved = fields.Boolean(string="Approved generic rules")

    @api.onchange("parent_id")
    def onchange_parent_id(self):
        if len(self.parent_id) > 0:
            self.representative = True
        else:
            self.representative = False
        return super().onchange_parent_id()

    @api.depends("subscription_request_ids.state")
    def _compute_coop_candidate(self):
        for partner in self:
            if partner.member:
                is_candidate = False
            else:
                sub_requests = partner.subscription_request_ids.filtered(
                    lambda record: record.state == "done"
                )
                is_candidate = bool(sub_requests)

            partner.coop_candidate = is_candidate

    @api.depends("parent_id", "parent_id.member", "representative")
    def _compute_representative_of_member_company(self):
        for partner in self:
            member_companies = self.env["res.partner"].search(
                [("is_company", "=", True), ("member", "=", True)]
            )
            representatives = member_companies.mapped("child_ids").filtered(
                "representative"
            )
            partner.representative_of_member_company = partner in representatives

    def has_representative(self):
        self.ensure_one()
        if self.child_ids.filtered("representative"):
            return True
        return False

    def get_representative(self):
        self.ensure_one()
        return self.child_ids.filtered("representative")

    def get_cooperator_from_email(self, email):
        if email:
            email = email.strip()
        # email could be falsy or be only made of whitespace.
        if not email:
            return self.browse()
        partner = self.search(
            [("cooperator", "=", True), ("email", "=", email)], limit=1
        )
        if not partner:
            partner = self.search([("email", "=", email)], limit=1)
        return partner

    def get_cooperator_from_crn(self, company_register_number):
        if company_register_number:
            company_register_number = company_register_number.strip()
        # company_register_number could be falsy or be only made of whitespace.
        if not company_register_number:
            return self.browse()
        partner = self.search(
            [
                ("cooperator", "=", True),
                ("company_register_number", "=", company_register_number),
            ],
            limit=1,
        )
        if not partner:
            partner = self.search(
                [("company_register_number", "=", company_register_number)], limit=1
            )
        return partner
