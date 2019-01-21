# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    coop_email_contact = fields.Char(string="Contact email address for the"
                                     " cooperator")
    subscription_maximum_amount = fields.Float(string="Maximum authorised"
                                               " subscription amount")
    default_country_id = fields.Many2one('res.country',
                                         string="Default country",
                                         default=lambda self: self.country_id)
    default_lang_id = fields.Many2one('res.lang',
                                      string="Default lang")
    board_representative = fields.Char(string="Board representative name")
    signature_scan = fields.Binary(string="Board representative signature")
    property_cooperator_account = fields.Many2one('account.account',
                                                  company_dependent=True,
                                                  string="Cooperator Account",
                                                  domain=[('internal_type', '=', 'receivable'),
                                                          ('deprecated', '=', False)],
                                                  help="This account will be"
                                                  " the default one as the"
                                                  " receivable account for the"
                                                  " cooperators",
                                                  required=True)
    unmix_share_type = fields.Boolean(string="Unmix share type",
                                      help="If checked, A cooperator will be"
                                      " authorised to have only one type"
                                      " of share")
    display_logo1 = fields.Boolean(string="Display logo 1")
    display_logo2 = fields.Boolean(string="Display logo 2")
    bottom_logo1 = fields.Binary(string="Bottom logo 1")
    bottom_logo2 = fields.Binary(string="Bottom logo 2")
