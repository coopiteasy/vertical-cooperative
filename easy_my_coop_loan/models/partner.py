from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loan_line_ids = fields.One2many('loan.issue.line',
                                    'partner_id',
                                    string="Loans")
