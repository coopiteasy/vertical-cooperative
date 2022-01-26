# Copyright 2021+ Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from calendar import monthrange

from odoo import api, fields, models


class WithholdingTaxDeclarationWizard(models.TransientModel):
    _name = "payment.report.wizard"
    _description = "Wizard to Compute Tax Withholding Declaration"

    @api.model
    def _default_date_start(self):
        date = fields.Date
        year = date.today().year
        month = date.today().month

        return date.to_date("{}-{}-{}".format(year, month, 1))

    @api.model
    def _default_date_end(self):
        date = fields.Date
        year = date.today().year
        month = date.today().month

        l_day = monthrange(year, month)[1]
        return date.to_date("{}-{}-{}".format(year, month, l_day))

    report_type = fields.Selection(
        [
            ("tax", "Withholding Tax Report"),
            ("reimbursement", "Loan reimbursement Report"),
        ],
        string="Report type",
        required=True,
    )
    date_start = fields.Date(
        string="Start Date", default=_default_date_start, required=True
    )
    date_end = fields.Date(string="Start End", default=_default_date_end, required=True)

    def _prepare_payment_report(self):
        interest_lines = self.env["loan.interest.line"].search(
            [
                ("due_date", ">=", self.date_start),
                ("due_date", "<=", self.date_end),
            ]
        )

        total_gross_interests = 0
        total_net_interests = 0
        total_withholding_tax = 0
        total_loan_amount = 0
        total_amount_due = 0

        for line in interest_lines:
            total_gross_interests += line.interest
            total_net_interests += line.net_interest
            total_withholding_tax += line.taxes_amount
            total_loan_amount += line.due_loan_amount
            total_amount_due += line.due_amount

        return {
            "report_type": self.report_type,
            "date_start": self.date_start,
            "date_end": self.date_end,
            "interest_lines": [(6, 0, interest_lines.ids)],
            "total_gross_interests": total_gross_interests,
            "total_net_interests": total_net_interests,
            "total_withholding_tax": total_withholding_tax,
            "total_loan_amount": total_loan_amount,
            "total_amount_due": total_amount_due,
        }

    def action_print_pdf(self):
        self.ensure_one()

        model = self.env["loan.interest.line.report"]
        report = model.create(self._prepare_payment_report())

        return report.print_report()
