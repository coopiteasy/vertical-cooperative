# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LoanEndOfYearOperation(models.TransientModel):
    _name = "loan.end.of.year.operation"
    _description = "Loan End of Year Operation"

    operation_type = fields.Selection(
        [
            ("eoy_operation", "End of year operation"),
            ("loan_due", "Reimbursement due operation"),
            ("payment_due", "Payment due operation"),
        ],
        required=True,
        string="Operation type",
    )
    ongoing_fy_id = fields.Many2one(
        comodel_name="account.fiscal.year", string="Ongoing fiscal year", required=True
    )
    due_date = fields.Date(string="Due date")

    @api.multi
    def run(self):
        self.ensure_one()
        afy_obj = self.env["account.fiscal.year"]
        interest_line_obj = self.env["loan.interest.line"]

        loan_issues = self.env["loan.issue"].browse(self._context.get("active_ids"))

        if self.operation_type == "eoy_operation":
            last_fy_day = self.ongoing_fy_id.date_to
            next_fy = afy_obj.get_next_fiscal_year(last_fy_day)
            if next_fy:
                interest_lines_loan = interest_line_obj.search(
                    [
                        ("due_date", ">=", next_fy.date_from),
                        ("due_date", "<=", next_fy.date_to),
                        ("due_loan_amount", ">", 0),
                        ("loan_issue_id", "in", loan_issues.ids),
                        ("loan_reimbursment_move", "=", False),
                    ]
                )

                interest_lines_loan.generate_loan_due_fy(last_fy_day)

                interest_lines = interest_line_obj.search(
                    [
                        ("due_date", ">=", next_fy.date_from),
                        ("due_date", "<=", next_fy.date_to),
                        ("interest", ">", 0),
                        ("loan_issue_id", "in", loan_issues.ids),
                        ("interest_closing_fy", "=", False),
                        ("interest_opening_fy", "=", False),
                    ]
                )

                interest_lines.generate_interest_move_lines_fy(last_fy_day, next_fy)
                (interest_lines + interest_lines_loan).write({"state": "due_fy"})
                if not interest_lines_loan and not interest_lines:
                    raise UserError(
                        _(
                            "There is no end of year account move"
                            " lines to generate for the selected loan"
                            " issue"
                        )
                    )
        elif self.operation_type == "loan_due":
            fy = afy_obj.get_next_fiscal_year()
            interest_lines = interest_line_obj.search(
                [
                    ("due_date", ">=", fy.date_from),
                    ("due_date", "<=", fy.date_to),
                    ("due_loan_amount", ">", 0),
                    ("loan_issue_id", "in", loan_issues.ids),
                    ("state", "=", "due_fy"),
                    ("loan_due_move", "=", False),
                ]
            )
            interest_lines.generate_loan_due_now()
        elif self.operation_type == "payment_due":
            fy = afy_obj.get_next_fiscal_year()
            interest_lines = interest_line_obj.search(
                [
                    ("due_date", ">=", fy.date_from),
                    ("due_date", "<=", fy.date_to),
                    ("loan_issue_id", "in", loan_issues.ids),
                    ("due_amount", ">", 0),
                    ("state", "=", "due"),
                ]
            )

            interest_lines.generate_payment_move_lines()
