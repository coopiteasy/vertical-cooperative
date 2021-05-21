# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    days_ahead = fields.Integer(
        string="Days ahead the due date",
        help="We are waiting x days before due date to create the "
        "reimbursement accounting entries creation",
    )
    awaiting_loan_payment_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Awaiting Loan Payment Account",
        domain=[
            ("internal_type", "=", "receivable"),
            ("deprecated", "=", False),
        ],
        help="This account serve to track awaiting payment."
        " It only serve a bank reconciliation purpose to register the awaiting"
        " loan payment as received/paid",
        required=True,
    )
    loaner_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Loaner Account",
        help="This account will be the default one as the"
        " receivable account for the cooperators",
        required=True,
    )
    debt_long_term_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Long Term Debt Account",
        help="This account is used to register the loan debt due for more"
        " than one year",
        required=True,
    )
    debt_long_term_fy_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Long Term Debt Due In The Year Account",
        help="This account is used to register the loan debt due for the"
        " current fiscal year",
        required=True,
    )
    debt_long_term_due_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Long Term Debt Due Account",
        help="This account is used to register the loan debt due",
        required=True,
    )
    expense_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Expense Account",
        help="This account is used to register the prorata temporis interest"
        " amount at the end of the fiscal year",
        required=True,
    )
    interest_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Interest Account",
        help="This account is used to register the due loan interest",
        required=True,
    )
    tax_account = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Tax Account",
        help="This account is used to register the tax to pay"
        " to the tax administration",
        required=True,
    )
    awaiting_loan_payment_journal = fields.Many2one(
        "account.journal",
        string="Awaiting loan payment journal",
        help="This journal will be the default one as the"
        " to track the payment from the loaners",
    )
    loan_journal = fields.Many2one(
        "account.journal",
        string="Loan journal",
        help="This journal will be the one used to register all"
        " the loan account move lines",
    )
