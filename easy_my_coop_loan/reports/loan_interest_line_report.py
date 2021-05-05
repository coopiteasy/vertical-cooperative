# Copyright 2021+ Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WithholdingTaxDeclarationReport(models.TransientModel):
    _name = "loan.interest.line.report"
    _description = "Loan Interest Line Report"

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    interest_lines = fields.Many2many(comodel_name='loan.interest.line')
    total_gross_interests = fields.Monetary(
        string="Total gross interests",
        currency_field="company_currency_id",
    )
    total_net_interests = fields.Monetary(
        string="Total net interests",
        currency_field="company_currency_id",
    )
    total_withholding_tax = fields.Monetary(
        string="Total Withholding Tax",
        currency_field="company_currency_id",
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )

    def print_report(self):
        self.ensure_one()
        context = dict(self.env.context)
        action = self.env.ref(
            "easy_my_coop_loan.action_withholding_tax_declaration_report"
        )
        return action.with_context(context).report_action(self, config=False)
