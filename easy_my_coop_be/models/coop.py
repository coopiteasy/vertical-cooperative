# -*- coding: utf-8 -*-
from openerp import fields, models


class subscription_request(models.Model):
    _inherit = 'subscription.request'

    company_type = fields.Selection(selection_add=[
                                    ('scrl', 'SCRL'),
                                    ('asbl', 'ASBL'),
                                    ('sprl', 'SPRL'),
                                    ('sa', 'SA')
                                    ])
