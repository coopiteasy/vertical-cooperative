# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _get_share_type(self):
        share_type_list = [('','')]
        for share_type in self.env['product.template'].search([('is_share','=',True)]):
            share_type_list.append((str(share_type.id),share_type.short_name))
        return share_type_list
    
    @api.multi
    @api.depends('share_ids')
    def _compute_effective_date(self):
        for partner in self:
            if partner.share_ids:
                partner.effective_date = partner.share_ids[0].effective_date  
    
    @api.multi
    @api.depends('share_ids')
    def _compute_cooperator_type(self):
        for partner in self:
            share_type = ''
            for line in partner.share_ids:
                share_type = str(line.share_product_id.id)
            if share_type != '': 
                partner.cooperator_type = share_type               

    @api.multi
    @api.depends('share_ids')
    def _compute_share_info(self):
        for partner in self:
            number_of_share = 0
            total_value =  0.0
            for line in partner.share_ids:
                number_of_share += line.share_number
                total_value += line.share_unit_price * line.share_number
            partner.number_of_share = number_of_share
            partner.total_value = total_value
     
    cooperator = fields.Boolean(string='Cooperator', help="Check this box if this contact is a cooperator(effective or not).")
    member = fields.Boolean(string='Effective cooperator', help="Check this box if this cooperator is an effective member.")
    old_member = fields.Boolean(string='Old cooperator', help="Check this box if this cooperator is no more an effective member.")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    national_register_number = fields.Char(string='National Register Number')
    share_ids = fields.One2many('share.line','partner_id',string='Share Lines')
    cooperator_register_number = fields.Integer(string='Cooperator Number')
    birthdate = fields.Date(string="Birthdate")
    number_of_share = fields.Integer(compute="_compute_share_info", multi='share', string='Number of share', readonly=True)
    total_value = fields.Float(compute="_compute_share_info", multi='share', string='Total value of shares', readonly=True)
    company_register_number = fields.Char(string='National Register Number')
    cooperator_type = fields.Selection(selection='_get_share_type', compute='_compute_cooperator_type', string='Cooperator Type', store=True)
    effective_date = fields.Date(sting="Effective Date", compute='_compute_effective_date', store=True)
    
    def get_cooperator_from_nin(self, national_id_number):
        return self.search([('cooperator','=',True),('national_register_number','=',national_id_number)])
    
    def get_cooperator_from_crn(self, company_register_number):
        return self.search([('cooperator','=',True),('company_register_number','=',company_register_number)])