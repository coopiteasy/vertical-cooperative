# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class subscription_request(models.Model):
    _inherit = 'subscription.request'
    
    def get_required_field(self):
        required_fields = super(subscription_request,self).get_required_field()
#         if 'no_registre' in required_fields:
#             required_fields.remove('no_registre')
        if 'iban' in required_fields:
            required_fields.remove('iban')
        
        return required_fields