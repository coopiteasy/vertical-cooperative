# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    customer = fields.Boolean(string='Become customer')
    eater = fields.Selection([('eater', 'Eater'), ('worker_eater', 'Worker and Eater')], string="Eater/Worker")