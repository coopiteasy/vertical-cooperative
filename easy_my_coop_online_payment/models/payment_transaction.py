# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):

    _inherit = 'payment.transaction'

    release_capital_request = fields.Many2one('account.invoice',
                                              string="Release Capital request")

    @api.model
    def process_online_payment_reception(self, tx):
        release_capital_request = tx.release_capital_request
        release_capital_request.subscription_request[0].state = 'paid'
        effective_date = datetime.now().strftime("%d/%m/%Y")
        release_capital_request.sudo().set_cooperator_effective(effective_date)

        return True

    @api.v7
    def _paypal_form_validate(self, cr, uid, tx, data, context=None):
        status = data.get('payment_status')
        res = {
            'acquirer_reference': data.get('txn_id'),
            'paypal_txn_type': data.get('payment_type'),
        }
        if status in ['Completed', 'Processed']:
            _logger.info('Validated Paypal payment for tx %s: set as done' % (tx.reference))
            res.update(state='done', date_validate=fields.Datetime.now())
            result = tx.write(res)
            self.process_online_payment_reception(cr, uid, tx)
            return result
        elif status in ['Pending', 'Expired']:
            _logger.info('Received notification for Paypal payment %s: set as pending' % (tx.reference))
            res.update(state='pending', state_message=data.get('pending_reason', ''))
            return tx.write(res)
        else:
            error = 'Received unrecognized status for Paypal payment %s: %s, set as error' % (tx.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return tx.write(res)
