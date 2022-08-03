import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LoanIssue(models.Model):
    _name = 'loan.issue'
    _description = 'Loan Issue'

    @api.multi
    def _compute_subscribed_amount(self):
        for issue in self:
            susbscribed_amount = 0.0
            for line in issue.loan_issue_lines.filtered(
                                lambda record: record.state != 'cancelled'):
                susbscribed_amount += line.amount
            issue.subscribed_amount = susbscribed_amount

    name = fields.Char(string="Name",
                       translate=True)
    is_bond = fields.Boolean(string="Is a bond issue?")
    is_loan = fields.Boolean(string="Is a subordinated loan issue?")
    default_issue = fields.Boolean(string="Default issue")
    subscription_start_date = fields.Date(string="Start date")
    subscription_end_date = fields.Date(string="End date")
    user_id = fields.Many2one('res.users',
                              string="Responsible")
    term_date = fields.Date(string="Term date")
    loan_term = fields.Float(string="term of the loan")
    rate = fields.Float(string="Interest rate")
    face_value = fields.Monetary(string="Facial value",
                                 currency_field='company_currency_id',
                                 required=True)
    minimum_amount = fields.Monetary(string="Minimum amount",
                                     currency_field='company_currency_id')
    maximum_amount = fields.Monetary(string="Maximum amount",
                                     currency_field='company_currency_id')
    maximum_amount_per_sub = fields.Monetary(
                            string="Maximum amount per subscription",
                            currency_field='company_currency_id')
    subscribed_amount = fields.Monetary(string="Subscribed amount",
                                        compute="_compute_subscribed_amount",
                                        currency_field='company_currency_id')
    interest_payment = fields.Selection([('end', 'End'),
                                         ('yearly', 'Yearly')],
                                        string="Interest payment")
    loan_issue_lines = fields.One2many('loan.issue.line',
                                       'loan_issue_id',
                                       string="Loan issue lines")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled'),
                              ('ongoing', 'Ongoing'),
                              ('closed', 'Closed')],
                             string="State",
                             default='draft')
    company_currency_id = fields.Many2one('res.currency',
                                          related='company_id.currency_id',
                                          string="Company Currency",
                                          readonly=True)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 required=True,
                                 readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get()) #noqa
    by_company = fields.Boolean(string="By company")
    by_individual = fields.Boolean(string='By individuals')
    display_on_website = fields.Boolean(sting='Display on website')
    taxes_rate = fields.Float(string="Taxes on interest",
                              required=True)

    @api.multi
    def toggle_display(self):
        for loan_issue in self:
            loan_issue.display_on_website = not loan_issue.display_on_website

    @api.multi
    def get_web_loan_issues(self, is_company):
        loan_issues = self.search([
                            ('is_loan', '=', True),
                            ('display_on_website', '=', True),
                            ('state', '=', 'ongoing')
                            ])
        if is_company is True:
            return loan_issues.filtered('by_company')
        else:
            return loan_issues.filtered('by_individual')

    @api.multi
    def get_web_bond_issues(self, is_company):
        bond_issues = self.search([
                            ('is_bond', '=', True),
                            ('display_on_website', '=', True),
                            ('state', '=', 'ongoing')
                            ])
        if is_company is True:
            return bond_issues.filtered('by_company')
        else:
            return bond_issues.filtered('by_company')

    @api.multi
    def get_web_issues(self, is_company):
        issues = self.get_web_loan_issues(is_company)
        issues = issues + self.get_web_bond_issues(is_company)
        return issues

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirmed'})

    @api.multi
    def action_open(self):
        self.ensure_one()
        self.write({'state': 'ongoing'})

    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})

    @api.multi
    def action_close(self):
        self.ensure_one()
        self.write({'state': 'closed'})

    def get_interest_vals(self, line, vals):
        interest_obj = self.env['loan.interest.line']
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
            vals['interest'] = interest
            vals['net_interest'] = net_interest
            vals['taxes_amount'] = taxes_amount
            vals['accrued_amount'] = accrued_amount
            vals['accrued_interest'] = accrued_interest
            vals['accrued_net_interest'] = accrued_net_interest
            vals['accrued_taxes'] = accrued_taxes
            vals['name'] = year
            interest_obj.create(vals)

    @api.multi
    def compute_loan_interest(self):
        self.ensure_one()

        if self.interest_payment == 'end':
            due_date = self.term_date
        for line in self.loan_issue_lines:
            # TODO remove this line
            line.interest_lines.unlink()
            # Please Do not Forget
            vals = {
                'issue_line': line.id,
                'due_date': due_date,
                'taxes_rate': self.taxes_rate
                }
            self.get_interest_vals(line, vals)

            rounded_term = int(self.loan_term)
            if self.loan_term - rounded_term > 0:
                # TODO Handle this case
                _logger.info("todo")
