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
    def _compute_subscribed_amount(self):
        for issue in self:
            susbscribed_amount = 0.0
            for line in issue.loan_issue_lines.filtered(
                lambda record: record.state != "cancelled"
            ):
                susbscribed_amount += line.amount
            issue.subscribed_amount = susbscribed_amount

    name = fields.Char(string="Name", translate=True)
    default_issue = fields.Boolean(string="Default issue")
    subscription_start_date = fields.Date(
        string="Start date subscription period"
    )
    subscription_end_date = fields.Date(string="End date subscription period")
    user_id = fields.Many2one("res.users", string="Responsible")
    loan_start_date = fields.Date(string="Loan start date")
    term_date = fields.Date(string="Term date")
    loan_term = fields.Float(string="Duration of the loan in month")
    rate = fields.Float(string="Interest rate")
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
        compute="_compute_subscribed_amount",
        currency_field="company_currency_id",
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
    )  # noqa
    by_company = fields.Boolean(string="By company")
    by_individual = fields.Boolean(string="By individuals")
    display_on_website = fields.Boolean(sting="Display on website")
    taxes_rate = fields.Float(string="Taxes on interest", required=True)

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
        bond_issues = self.search(
            [("display_on_website", "=", True), ("state", "=", "ongoing")]
        )
        if is_company is True:
            return bond_issues.filtered("by_company")
        else:
            return bond_issues.filtered("by_company")

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

    def get_interest_vals(self, line, vals):
        interest_obj = self.env["loan.interest.line"]
        accrued_amount = line.amount
        accrued_interest = 0
        accrued_net_interest = 0
        accrued_taxes = 0
        for year in range(1, int(self.loan_term) + 1):
            interest = accrued_amount * (line.loan_issue_id.rate / 100)
            accrued_amount += interest
            taxes_amount = interest * (self.taxes_rate / 100)
            net_interest = interest - taxes_amount
            accrued_interest += interest
            accrued_net_interest += net_interest
            accrued_taxes += taxes_amount
            vals["interest"] = interest
            vals["net_interest"] = net_interest
            vals["taxes_amount"] = taxes_amount
            vals["accrued_amount"] = accrued_amount
            vals["accrued_interest"] = accrued_interest
            vals["accrued_net_interest"] = accrued_net_interest
            vals["accrued_taxes"] = accrued_taxes
            vals["name"] = year
            interest_obj.create(vals)

    @api.multi
    def compute_loan_interest(self):
        self.ensure_one()

        if self.interest_payment == "end":
            due_date = self.term_date
        else:
            raise NotImplementedError(
                _("Interest payment by year hasn't been " "implemented yet")
            )
        for line in self.loan_issue_lines:
            # TODO remove this line
            line.interest_lines.unlink()
            # Please Do not Forget
            vals = {
                "issue_line": line.id,
                "due_date": due_date,
                "taxes_rate": self.taxes_rate,
            }
            self.get_interest_vals(line, vals)

            rounded_term = int(self.loan_term)
            if self.loan_term - rounded_term > 0:
                # TODO Handle this case
                raise NotImplementedError(
                    _(
                        "Calculation on non entire year "
                        "hasn't been implemented yet"
                    )
                )
