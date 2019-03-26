# -*- coding: utf-8 -*-
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    eater = fields.Selection([('eater', 'Eater'),
                              ('worker_eater', 'Worker and Eater')],
                             string="Eater/Worker")
