# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import api, fields, models, _

class TaxShelterCertificate(models.Model):
    _name="tax.shelter.declaration"
    
    declaration_year = fields.Integer(string='Declaration year', required=True)
    tax_shelter_certificates = fields.One2many('tax.shelter.certificate','declaration_id', string='Tax shelter certificates', readonly=True)
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    tax_shelter_percentage = fields.Selection([('30','30%'),
                                               ('45','45%')],
                                              string='Tax Shelter percentage', required=True)
    
    @api.one
    def process_declaration(self):
        True
        
class TaxShelterCertificate(models.Model):
    _name="tax.shelter.certificate"
    
    partner_id = fields.Many2one('res.partner', string='Cooperator', required=True, readonly=True)
    declaration_id = fields.Many2one('tax.shelter.declaration', string='Declaration', required=True, readonly=True) 
    subscribed_lines = fields.One2many('certificate.line','tax_shelter_certificate', string='Certificate lines', readonly=True)
    sell_back_lines = fields.One2many('certificate.line','tax_shelter_certificate', string='Shares resold', readonly=True)
    total = fields.Float(string='Total')
    
        
class TaxShelterCertificateLine(models.Model):
    _name="certificate.line"
    
    tax_shelter_certificate = fields.Many2one('tax.shelter.certificate', string="Tax shelter certificate",required=True)
    share_type = fields.Many2one('product.produt', string='Share type', required=True, readonly=True)
    share_price = fields.Float(string='Share price', required=True, readonly=True)
    quantity = fields.Integer(string='Number of shares', required=True, readonly=True)
    transaction_date = fields.Date(string="Transaction date")
    certificat_type = fields.Selection([('subscribed','Subscribed'),
                                       ('resold','Resold'),
                                       ('kept','Kept')], required=True, readonly=True) 
    total = fields.Float(compute='_compute_total', string='Sub total')
    
    @api.multi
    def _compute_total(self):
        for line in self:
            total = line.share_price * line.quantity