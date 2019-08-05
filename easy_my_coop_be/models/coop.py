from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    company_type = fields.Selection([('scrl', 'SCRL'),
                                     ('asbl', 'ASBL'),
                                     ('sprl', 'SPRL'),
                                     ('sa', 'SA')])
