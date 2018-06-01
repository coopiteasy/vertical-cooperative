# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class subscription_request(models.Model):
    _inherit = 'subscription.request'
    
    company_type = fields.Selection([('ei','Individual company'),
                                     ('snc','Partnership'),
                                     ('sa','Limited company (SA)'),
                                     ('sarl','Limited liability company (Ltd)'),
                                     ('sc','Cooperative'),
                                     ('asso','Association'),
                                     ('fond','Foundation'),
                                     ('edp','Company under public law')])
        
#     def get_required_field(self):
#         required_fields = super(subscription_request,self).get_required_field()
#         if 'iban' in required_fields:
#             required_fields.remove('iban')
#         
#         return required_fields

    def check_belgian_identification_id(self, nat_register_num):
        #deactivate number validation for swiss localization
        return True