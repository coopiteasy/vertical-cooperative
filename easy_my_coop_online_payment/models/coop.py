# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    payment_type = fields.Selection([('online', 'Online'),
                                     ('deferred', 'Deferred')], string='Payment Type')
    
    def send_capital_release_request(self, invoice):
        if self.payment_type == 'deferred':
            super(SubscriptionRequest, self).send_capital_release_request(invoice)
        return True