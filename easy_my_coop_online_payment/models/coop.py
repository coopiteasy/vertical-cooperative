# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class subscription_request(models.Model):
    _inherit = 'subscription.request'

    payment_type = fields.Selection([('online', 'Online'),
                                     ('deferred', 'Deferred')], string='Payment Type')