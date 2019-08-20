
from datetime import datetime

from odoo import api, fields, models


class LoanIssueLine(models.Model):
    _name = 'loan.issue.line'
    _order = 'date desc, id'

    @api.multi
    @api.depends('quantity', 'face_value')
    def _compute_amount(self):
        for line in self:
            line.amount = line.face_value * line.quantity

    name = fields.Char(string="Reference")
    loan_issue_id = fields.Many2one('loan.issue',
                                    string="Loan issue",
                                    required=True)
    interest_lines = fields.One2many('loan.interest.line',
                                     'issue_line',
                                     string="Interest lines")
    quantity = fields.Integer(string='quantity',
                              required=True)
    face_value = fields.Monetary(related='loan_issue_id.face_value',
                                 currency_field='company_currency_id',
                                 store=True,
                                 readonly=True)
    partner_id = fields.Many2one('res.partner',
                                 string="Subscriber",
                                 required=True)
    date = fields.Date(string="Subscription date",
                       default=lambda self: datetime.strftime(datetime.now(),
                                                              '%Y-%m-%d'),
                       required=True)
    amount = fields.Monetary(string="Subscribed amount",
                             currency_field='company_currency_id',
                             compute='_compute_amount',
                             store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('subscribed', 'Subscribed'),
                              ('waiting', 'Waiting payment'),
                              ('paid', 'paid'),
                              ('cancelled', 'Cancelled'),
                              ('ended', 'Ended')],
                             string="State",
                             required=True,
                             default="draft")
    company_currency_id = fields.Many2one('res.currency',
                                          related='company_id.currency_id',
                                          string="Company Currency",
                                          readonly=True)
    company_id = fields.Many2one('res.company',
                                 related='loan_issue_id.company_id',
                                 string="Company",
                                 readonly=True)

    def create(self, vals):
        mail_template = 'easy_my_coop_loan.loan_subscription_confirmation'
        confirmation_mail_template = self.env.ref(mail_template, False)

        line = super(LoanIssueLine, self).create(vals)
        confirmation_mail_template.send_mail(line.id)

        return line

    @api.multi
    def action_draft(self):
        for line in self:
            line.write({'state': 'draft'})

    @api.multi
    def action_validate(self):
        for line in self:
            line.write({'state': 'subscribed'})

    @api.multi
    def action_request_payment(self):
        mail_template = 'easy_my_coop_loan.loan_issue_payment_request'
        pay_req_mail_template = self.env.ref(mail_template, False)

        for line in self:
            pay_req_mail_template.send_mail(line.id)
            line.write({'state': 'waiting'})

    @api.multi
    def action_cancel(self):
        for line in self:
            line.write({'state': 'cancelled'})

    @api.multi
    def action_paid(self):
        for line in self:
            line.write({'state': 'paid'})
