# -*- coding: utf-8 -*-
from openerp import fields, models


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    company_type = fields.Selection([
                            ('asso', 'Association'),
                            ('eurl', 'EURL / Entreprise individuelle'),
                            ('sarl', 'SARL'),
                            ('sa', 'SA / SAS')])

    def get_required_field(self):
        req_fields = super(SubscriptionRequest, self).get_required_field()
        if 'iban' in req_fields:
            req_fields.remove('iban')

        return req_fields

    # override function to disable the check
    def check_belgian_identification_id(self, nat_register_num):
        # deactivate number validation for french localization
        return True
