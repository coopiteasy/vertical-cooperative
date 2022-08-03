# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class LoanIssue(models.Model):
    _name = "loan.issue"
    _description = "Loan Issue"

    @api.multi
    def _compute_amounts(self):
        for issue in self:
            subscription_lines = issue.loan_issue_lines.filtered(
                lambda line: line.state != "cancelled"
            )
            issue.subscribed_amount = sum(subscription_lines.mapped("amount"))

            paid_lines = issue.loan_issue_lines.filtered(
                lambda line: line.state == "paid"
            )
            issue.paid_amount = sum(paid_lines.mapped("amount"))

    name = fields.Char(string="Name", translate=True)
    default_issue = fields.Boolean(string="Default issue")
    subscription_start_date = fields.Date(string="Start date subscription period")
    subscription_end_date = fields.Date(string="End date subscription period")
    user_id = fields.Many2one("res.users", string="Responsible")
    loan_start_date = fields.Date(string="Loan start date")
    term_date = fields.Date(string="Term date")
    loan_term = fields.Float(string="Duration of the loan in month", required=True)
    rate = fields.Float(string="Net Interest rate")
    gross_rate = fields.Float(string="Gross Interest rate")
    taxes_rate = fields.Float(string="Taxes on interest", required=True)
    face_value = fields.Monetary(
        string="Facial value",
        currency_field="company_currency_id",
        required=True,
    )
    minimum_amount = fields.Monetary(
        string="Minimum amount of issue", currency_field="company_currency_id"
    )
    maximum_amount = fields.Monetary(
        string="Maximum amount of issue", currency_field="company_currency_id"
    )
    min_amount_company = fields.Monetary(
        string="Minimum amount for a company",
        currency_field="company_currency_id",
    )
    max_amount_company = fields.Monetary(
        string="Maximum amount for a company",
        currency_field="company_currency_id",
    )
    min_amount_person = fields.Monetary(
        string="Minimum amount for a person",
        currency_field="company_currency_id",
    )
    max_amount_person = fields.Monetary(
        string="Maximum amount for a person",
        currency_field="company_currency_id",
    )
    subscribed_amount = fields.Monetary(
        string="Subscribed amount",
        compute="_compute_amounts",
        currency_field="company_currency_id",
    )
    paid_amount = fields.Monetary(
        string="Paid amount",
        compute="_compute_amounts",
        currency_field="company_currency_id",
    )
    capital_payment = fields.Selection(
        [("end", "End"), ("yearly", "Yearly")], string="Capital reimbursement"
    )
    interest_payment = fields.Selection(
        [("end", "End"), ("yearly", "Yearly")], string="Interest payment"
    )
    interest_payment_info = fields.Char(string="Yearly payment on")
    loan_issue_lines = fields.One2many(
        "loan.issue.line", "loan_issue_id", string="Loan issue lines"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("ongoing", "Ongoing"),
            ("closed", "Closed"),
        ],
        string="State",
        default="draft",
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
    by_company = fields.Boolean(string="By company")
    by_individual = fields.Boolean(string="By individuals")
    display_on_website = fields.Boolean(sting="Display on website")

    @api.multi
    def get_max_amount(self, partner):
        """
        Return the maximum amount that partner can buy.
        A negative value means that there is no maximum.
        """
        self.ensure_one()
        lines = self.loan_issue_lines.filtered(
            lambda r: r.partner_id == partner and r.state != "cancelled"
        )
        already_subscribed = sum(line.amount for line in lines)
        max_amount = -1  # No max amount
        if partner.is_company and self.max_amount_company > 0:
            max_amount = max(0, self.max_amount_company - already_subscribed)
        if not partner.is_company and self.max_amount_person > 0:
            max_amount = max(0, self.max_amount_person - already_subscribed)
        return max_amount

    @api.multi
    def get_min_amount(self, partner):
        """
        Return the minimum amount that a partner must buy.
        A zero value means that there is no minimum amount.
        """
        self.ensure_one()
        lines = self.loan_issue_lines.filtered(
            lambda r: r.partner_id == partner and r.state != "cancelled"
        )
        amount_subscribed = sum(line.amount for line in lines)
        if partner.is_company:
            min_amount = self.min_amount_company - amount_subscribed
        else:
            min_amount = self.min_amount_person - amount_subscribed
        return max(0, min_amount)

    @api.multi
    def get_web_issues(self, is_company):
        loan_issues = self.search(
            [("display_on_website", "=", True), ("state", "=", "ongoing")]
        )
        if is_company is True:
            return loan_issues.filtered("by_company")
        else:
            return loan_issues.filtered("by_company")

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.write({"state": "confirmed"})

    @api.multi
    def action_open(self):
        self.ensure_one()
        self.write({"state": "ongoing"})

    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.write({"state": "draft"})

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.write({"state": "cancelled"})

    @api.multi
    def action_close(self):
        self.ensure_one()
        self.write({"state": "closed"})

    @api.multi
    def compute_loan_interest(self):
        self.ensure_one()
        loan_term_year = self.loan_term / 12
        if not (loan_term_year).is_integer():
            # TODO Handle this case
            raise NotImplementedError(
                _("Calculation on non entire year " "hasn't been implemented yet")
            )

        lines = self.loan_issue_lines.filtered(lambda record: record.state == "paid")
        lines.action_compute_interest()

    def _cron_check_subscription_end_date(self):
        today = fields.Date.today()
        loans_to_close = self.search(
            [("state", "!=", "closed"), ("subscription_end_date", "<=", today)]
        )
        for loan in loans_to_close:
            try:
                loan.action_close()
                self.env.cr.commit()  # pylint: disable=invalid-commit
                _logger.debug("Loan: '{}' - state: '{}'".format(loan, loan.state))
            except Exception:
                _logger.exception(
                    "An exception occured while closing loan: '%s'" % (loan)
                )
                self.env.cr.rollback()
