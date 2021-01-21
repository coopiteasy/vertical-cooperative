# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        if self.member:
            return "Cooperator Certificate - %s" % self.name
        else:
            return "unknown"

    @api.multi
    def _invoice_total(self):
        account_invoice_report = self.env["account.invoice.report"]
        if not self.ids:
            self.total_invoiced = 0.0
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            # price_total is in the company currency
            all_partners_and_children[partner] = self.search(
                [("id", "child_of", partner.id)]
            ).ids
            all_partner_ids += all_partners_and_children[partner]

        # searching account.invoice.report via the orm is comparatively
        # expensive (generates queries "id in []" forcing to build the
        # full table).
        # In simple cases where all invoices are in the same currency than
        # the user's company access directly these elements

        # generate where clause to include multicompany rules
        where_query = account_invoice_report._where_calc(
            [
                ("partner_id", "in", all_partner_ids),
                ("state", "not in", ["draft", "cancel"]),
                ("company_id", "=", self.env.user.company_id.id),
                ("type", "in", ("out_invoice", "out_refund")),
                ("release_capital_request", "=", False),
            ]
        )
        account_invoice_report._apply_ir_rules(where_query, "read")
        from_clause, where_clause, where_clause_params = where_query.get_sql()

        # fixme while you're here, please fix the query
        #  to pass pylint sql-injection
        #  Note de Houssine: note que c'est la
        #  surcharge d'une fonction standard de la facturation Odoo. Elle
        #  date de la 9 voir si la v12 a été adaptée où est équivalente à la 12
        # price_total is in the company currency pylint:
        # pylint: disable=sql-injection
        query = (
            """
                SELECT SUM(price_total) as total, partner_id
                FROM account_invoice_report account_invoice_report
                WHERE %s
                GROUP BY partner_id
                """
            % where_clause
        )

        self.env.cr.execute(query, where_clause_params)
        price_totals = self.env.cr.dictfetchall()
        for partner, child_ids in all_partners_and_children.items():
            partner.total_invoiced = sum(
                price["total"]
                for price in price_totals
                if price["partner_id"] in child_ids
            )

    @api.multi
    @api.depends("share_ids")
    def _compute_effective_date(self):
        # TODO change it to compute it from the share register
        for partner in self:
            if partner.share_ids:
                partner.effective_date = partner.share_ids[0].effective_date

    @api.multi
    def _get_share_type(self):
        shares = self.env["product.product"].search([("is_share", "=", True)])
        share_types = [(s.default_code, s.short_name) for s in shares]
        return [("", "")] + share_types

    @api.multi
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

    @api.multi
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
        help="Check this box if this contact is a"
        " cooperator (effective or not).",
    )
    member = fields.Boolean(
        string="Effective cooperator",
        help="Check this box if this cooperator" " is an effective member.",
    )
    coop_candidate = fields.Boolean(
        string="Cooperator candidate",
        compute="_compute_coop_candidate",
        store=True,
        readonly=True,
    )
    old_member = fields.Boolean(
        string="Old cooperator",
        help="Check this box if this cooperator is"
        " no more an effective member.",
    )
    # todo use oca partner_contact_gender
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Gender",
    )
    share_ids = fields.One2many(
        "share.line", "partner_id", string="Share Lines"
    )
    cooperator_register_number = fields.Integer(string="Cooperator Number")
    number_of_share = fields.Integer(
        compute="_compute_share_info",
        multi="share",
        string="Number of share",
        readonly=True,
    )
    total_value = fields.Float(
        compute="_compute_share_info",
        multi="share",
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
        sting="Effective Date", compute=_compute_effective_date, store=True
    )
    representative = fields.Boolean(string="Legal Representative")
    representative_of_member_company = fields.Boolean(
        string="Legal Representative of Member Company",
        store=True,
        compute="_compute_representative_of_member_company",
    )
    subscription_request_ids = fields.One2many(
        "subscription.request", "partner_id", string="Subscription request"
    )
    legal_form = fields.Selection([("", "")], string="Legal form")
    data_policy_approved = fields.Boolean(string="Approved Data Policy")
    internal_rules_approved = fields.Boolean(string="Approved Internal Rules")
    financial_risk_approved = fields.Boolean(string="Approved Financial Risk")

    @api.multi
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

    @api.multi
    @api.depends("parent_id", "parent_id.member", "representative")
    def _compute_representative_of_member_company(self):
        for partner in self:
            member_companies = self.env["res.partner"].search(
                [("is_company", "=", True), ("member", "=", True)]
            )
            representatives = member_companies.mapped("child_ids").filtered(
                "representative"
            )
            partner.representative_of_member_company = (
                partner in representatives
            )

    @api.multi
    def has_representative(self):
        self.ensure_one()
        if self.child_ids.filtered("representative"):
            return True
        return False

    @api.multi
    def get_representative(self):
        self.ensure_one()
        return self.child_ids.filtered("representative")

    def get_cooperator_from_email(self, email):
        partner = self.search([('cooperator', '=', True),
                               ('email', '=', email)], limit=1)
        if not partner:
            partner = self.search([('email', '=', email)], limit=1)
        return partner

    def get_cooperator_from_crn(self, company_register_number):
        company_register_number = company_register_number.strip()
        partner = self.search([
            ('cooperator', '=', True),
            ('company_register_number', '=', company_register_number)
            ], limit=1)
        if not partner:
            partner = self.search([
                ('company_register_number', '=', company_register_number)
                ], limit=1)
        return partner
