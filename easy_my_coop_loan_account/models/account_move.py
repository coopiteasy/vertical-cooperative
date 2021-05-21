# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    loan_issue_line = fields.One2many(
        "loan.issue.line",
        "awaiting_move_id",
        string="Loan issue line",
        readonly=True,
    )

    loan_interest_line = fields.One2many(
        "loan.interest.line",
        "loan_reimbursment_move",
        string="Loan interest line",
        readonly=True,
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    loan_issue_line = fields.One2many(
        "loan.issue.line",
        related="move_id.loan_issue_line",
    )
    loan_interest_line = fields.One2many(
        "loan.interest.line",
        related="move_id.loan_interest_line",
    )

    @api.multi
    def check_full_reconcile(self):
        super(AccountMoveLine, self).check_full_reconcile()

        full_reconcile_id = self.mapped("full_reconcile_id")
        loan_issue_line = self.mapped("loan_issue_line")
        loan_interest_line = self.mapped("loan_interest_line")

        if full_reconcile_id and loan_issue_line:
            for move_line in self:
                if move_line.statement_id:
                    loan_issue_line.payment_date = move_line.date
            loan_issue_line.with_context({"paid_by_bank_statement": True}).action_paid()
        if full_reconcile_id and loan_interest_line:
            for move_line in self:
                if move_line.statement_id:
                    loan_interest_line.payment_date = move_line.date
            loan_interest_line.with_context(
                {"paid_by_bank_statement": True}
            ).action_paid()
