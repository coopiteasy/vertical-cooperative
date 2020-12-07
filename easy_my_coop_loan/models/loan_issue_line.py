# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LoanIssueLine(models.Model):
    _name = "loan.issue.line"
    _description = "Loan Issue Line"
    _order = "date desc, id"

    @api.multi
    @api.depends("quantity", "face_value")
    def _compute_amount(self):
        for line in self:
            line.amount = line.face_value * line.quantity

    name = fields.Char(string="Reference")
    loan_issue_id = fields.Many2one(
        "loan.issue", string="Loan issue", required=True
    )
    interest_lines = fields.One2many(
        "loan.interest.line", "issue_line", string="Interest lines"
    )
    quantity = fields.Integer(string="quantity", required=True)
    face_value = fields.Monetary(
        related="loan_issue_id.face_value",
        currency_field="company_currency_id",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        "res.partner", string="Subscriber", required=True
    )
    date = fields.Date(
        string="Subscription date",
        default=lambda self: datetime.strftime(datetime.now(), "%Y-%m-%d"),
        required=True,
    )
    amount = fields.Monetary(
        string="Subscribed amount",
        currency_field="company_currency_id",
        compute="_compute_amount",
        store=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("subscribed", "Subscribed"),
            ("waiting", "Waiting payment"),
            ("paid", "paid"),
            ("cancelled", "Cancelled"),
            ("ended", "Ended"),
        ],
        string="State",
        required=True,
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
        related="loan_issue_id.company_id",
        string="Company",
        readonly=True,
    )

    def get_loan_sub_mail_template(self):
        return self.env.ref(
            "easy_my_coop_loan.loan_subscription_confirmation", False
        )

    def get_loan_pay_req_mail_template(self):
        return self.env.ref(
            "easy_my_coop_loan.loan_issue_payment_request", False
        )

    @api.model
    def create(self, vals):
        line = super(LoanIssueLine, self).create(vals)

        confirmation_mail_template = line.get_loan_sub_mail_template()
        confirmation_mail_template.send_mail(line.id)

        return line

    @api.multi
    def action_draft(self):
        if self.filtered(lambda l: l.state != "cancelled"):
            raise ValidationError(
                _("You can only set cancelled loans to draft")
            )
        self.write({"state": "draft"})

    @api.multi
    def action_validate(self):
        if self.filtered(lambda l: l.state != "draft"):
            raise ValidationError(_("You can only validate draft loans"))
        self.write({"state": "subscribed"})

    @api.multi
    def action_request_payment(self):
        if self.filtered(lambda l: l.state != "subscribed"):
            raise ValidationError(
                _("You can only request payment for validated loans")
            )

        for line in self:
            pay_req_mail_template = line.get_loan_pay_req_mail_template()
            pay_req_mail_template.send_mail(line.id)
            line.write({"state": "waiting"})

    @api.multi
    def action_cancel(self):
        allowed_states = ["draft", "subscribed", "waiting"]
        if self.filtered(lambda l: l.state not in allowed_states):
            raise ValidationError(
                _(
                    "You can only cancel loans in states draft, "
                    "subscribed or waiting for payment."
                )
            )
        self.write({"state": "cancelled"})

    @api.multi
    def get_confirm_paid_email_template(self):
        self.ensure_one()
        return self.env.ref(
            "easy_my_coop_loan.email_template_loan_confirm_paid"
        )

    @api.multi
    def action_paid(self):
        if self.filtered(lambda l: l.state != "waiting"):
            raise ValidationError(
                _("You can only park as paid loans waiting for payment")
            )

        for line in self:
            loan_email_template = line.get_confirm_paid_email_template()
            loan_email_template.sudo().send_mail(line.id, force_send=False)

            line.write({"state": "paid"})
