# -*- coding: utf-8 -*-
from openerp import fields, models


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    payment_type = fields.Selection([('online', 'Online'),
                                     ('deferred', 'Deferred')],
                                    string='Payment Type',
                                    default="deferred")

    def send_capital_release_request(self, inv):
        if self.payment_type == 'deferred':
            super(SubscriptionRequest, self).send_capital_release_request(inv)
        return True


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def post_process_confirm_paid(self, effective_date):
        if self.subscription_request.payment_type == 'deferred':
            self.set_cooperator_effective(effective_date)

        return True
