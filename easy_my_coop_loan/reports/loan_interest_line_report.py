# Copyright 2021+ Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WithholdingTaxDeclarationReport(models.TransientModel):
    _name = "loan.interest.line.report"
    _description = "Loan Interest Line Report"

    report_type = fields.Selection(
        [
            ("tax", "Withholding Tax Report"),
            ("reimbursement", "Loan reimbursement Report"),
        ],
        string="Report type",
        required=True,
    )
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    interest_lines = fields.Many2many(comodel_name="loan.interest.line")
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
    total_loan_amount = fields.Monetary(
        string="Total Loan Amount",
        currency_field="company_currency_id",
    )
    total_amount_due = fields.Monetary(
        string="Total Amount Due",
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
        if self.report_type == "tax":
            report = (
                "easy_my_coop_loan.action_withholding_tax_declaration_report"  # noqa
            )
        elif self.report_type == "reimbursement":
            report = "easy_my_coop_loan.action_loan_reimbursement_report"
        action = self.env.ref(report)

        return action.with_context(context).report_action(self, config=False)
