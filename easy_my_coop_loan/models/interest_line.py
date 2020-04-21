# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class LoanInterestLine(models.Model):
    _name = "loan.interest.line"
    _description = "Loan Interest Line"

    name = fields.Integer(string="Year", required=True)
    issue_line = fields.Many2one(
        "loan.issue.line", string="Subscribed loan", required=True
    )
    partner_id = fields.Many2one(
        related="issue_line.partner_id", store=True, readlonly=True
    )
    amount = fields.Monetary(
        related="issue_line.amount",
        string="Subscribed amount",
        currency_field="company_currency_id",
        readonly=True,
    )
    interest = fields.Monetary(
        string="Gross interest amount",
        currency_field="company_currency_id",
        readonly=True,
    )
    net_interest = fields.Monetary(
        string="Net interest amount",
        currency_field="company_currency_id",
        readonly=True,
    )
    taxes_rate = fields.Float(string="Taxes on interest", required=True)
    taxes_amount = fields.Monetary(
        string="Taxes amount",
        currency_field="company_currency_id",
        readonly=True,
    )
    accrued_amount = fields.Monetary(
        string="Accrued amount",
        currency_field="company_currency_id",
        readonly=True,
    )
    accrued_interest = fields.Monetary(
        string="Accrued gross interest",
        currency_field="company_currency_id",
        readonly=True,
    )
    accrued_net_interest = fields.Monetary(
        string="Accrued net interest",
        currency_field="company_currency_id",
        readonly=True,
    )
    accrued_taxes = fields.Monetary(
        string="Accrued taxes to pay",
        currency_field="company_currency_id",
        readonly=True,
    )
    due_date = fields.Date(string="Due date")
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="issue_line.company_id",
        string="Company",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("due", "Due"),
            ("requested", "Payment requested"),
            ("donation", "Donation"),
            ("paid", "Paid"),
        ],
        string="State",
        default="draft",
    )
