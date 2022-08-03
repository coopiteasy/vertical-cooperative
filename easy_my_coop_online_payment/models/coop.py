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
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
        
    def post_process_confirm_paid(self, effective_date):
        if self.subscription_request.payment_type == 'deferred':
            self.set_cooperator_effective(effective_date) 
               
        return True