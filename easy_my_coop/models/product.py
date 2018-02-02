# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_share = fields.Boolean(string='Is share?')
    short_name = fields.Char(string='Short name')
    display_on_website = fields.Boolean(string='Display on website')
    default_share_product = fields.Boolean(string='Default share product')
    minimum_quantity = fields.Integer(string='Minimum quantity', default=1)
    force_min_qty = fields.Boolean(String="Force minimum quantity?")
    by_company = fields.Boolean(string="Can be subscribed by companies?")
    by_individual = fields.Boolean(string="Can be subscribed by individuals?")
    customer = fields.Boolean(string='Become customer')
    
    @api.multi
    def get_web_share_products(self, is_company):
        if is_company == True:
            product_templates = self.env['product.template'].search([('is_share','=',True), ('display_on_website','=',True),('by_company','=',True)])
        else:
            product_templates = self.env['product.template'].search([('is_share','=',True), ('display_on_website','=',True),('by_individual','=',True)])
        return product_templates
