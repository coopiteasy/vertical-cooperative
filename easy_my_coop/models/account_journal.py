# -*- coding: utf-8 -*-

from openerp import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    get_cooperator_payment = fields.Boolean('Get cooperator payments?')
    get_general_payment = fields.Boolean('Get general payments?')