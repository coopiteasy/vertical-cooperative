# -*- coding: utf-8 -*-
from openerp import fields, models


class subscription_request(models.Model):
    _inherit = 'subscription.request'

    company_type = fields.Selection([('ei', 'Individual company'),
                                     ('snc', 'Partnership'),
                                     ('sa', 'Limited company (SA)'),
                                     ('sarl', 'Limited liability company (Ltd)'), #noqa
                                     ('sc', 'Cooperative'),
                                     ('asso', 'Association'),
                                     ('fond', 'Foundation'),
                                     ('edp', 'Company under public law')])

    def get_required_field(self):
        req_fields = super(subscription_request, self).get_required_field()
        if 'no_registre' in req_fields:
            req_fields.remove('no_registre')

        return req_fields

    def check_belgian_identification_id(self, nat_register_num):
        # deactivate number validation for swiss localization
        return True
