# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import api, fields, models, _

TYPE_MAP = {
    'subscription':'subscribed',
    'transfer':'transfered',
    'sell_back':'resold'
}

class TaxShelterDeclaration(models.Model):
    _name = "tax.shelter.declaration"
    
    name = fields.Char(string='Declaration year', required=True)
    tax_shelter_certificates = fields.One2many('tax.shelter.certificate','declaration_id', string='Tax shelter certificates', readonly=True)
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    tax_shelter_percentage = fields.Selection([('30','30%'),
                                               ('45','45%')],
                                              string='Tax Shelter percentage', required=True)
    state = fields.Selection([('draft','Draft'),
                              ('computed','Computed'),
                              ('validated','Validated')], 
                              string='State',required=True, default="draft")

    def _prepare_line(self, certificate, entry):
        line_vals = {}
        line_vals['tax_shelter_certificate'] = certificate.id
        line_vals['share_type'] = entry.share_product_id.id
        line_vals['share_short_name'] = entry.share_short_name
        line_vals['share_unit_price'] = entry.share_unit_price
        line_vals['quantity'] = entry.quantity
        line_vals['transaction_date'] = entry.date
        line_vals['type'] = TYPE_MAP[entry.type]
        return line_vals
    
    @api.one
    def compute_declaration(self):
        entries = self.env['subscription.register'].search([('date','>=',self.date_from),
                                                            ('date','<=',self.date_to),
                                                            ('type','in',['subscription','sell_back','transfer'])])
        partner_certificate = {}
        for entry in entries:
            certificate = partner_certificate.get(entry.partner_id.id, False)
            if not certificate:
                #create a certificate for this cooperator
                cert_vals={}
                cert_vals['declaration_id'] = self.id
                cert_vals['partner_id'] = entry.partner_id.id
                cert_vals['cooperator_number'] = entry.partner_id.cooperator_register_number
                certificate = self.env['tax.shelter.certificate'].create(cert_vals)
                partner_certificate[entry.partner_id.id] = certificate
            line_vals = self._prepare_line(certificate, entry)
            self.env['certificate.line'].create(line_vals)
    
    @api.one    
    def validate_declaration(self):
        self.state = 'validated'
    
    @api.one
    def reset_declaration(self):
        if not self.state == 'validated':
            self.tax_shelter_certificates.unlink()
        
class TaxShelterCertificate(models.Model):
    _name = "tax.shelter.certificate"
    
    _order = "cooperator_number asc"
    
    cooperator_number = fields.Integer(string='Cooperator number', required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cooperator', required=True, readonly=True)
    state = fields.Selection([('draft','Draft'),
                              ('validated','Validated'),
                              ('sent','Sent')], 
                              string='State',required=True, default="draft")
    declaration_id = fields.Many2one('tax.shelter.declaration', string='Declaration', required=True, readonly=True) 
    lines = fields.One2many('certificate.line','tax_shelter_certificate', string='Certificate lines', readonly=True)
    subscribed_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Shares subscribed', readonly=True)
    resold_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Shares resold', readonly=True)
    transfered_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Shares transfered', readonly=True)
    total_amount_subscribed = fields.Float(compute='_compute_amounts', string='Total subscribed')
    total_amount_resold = fields.Float(compute='_compute_amounts', string='Total resold')
    total_amount_transfered = fields.Float(compute='_compute_amounts', string='Total transfered')
    total_amount = fields.Float(compute='_compute_amounts', string='Total', readonly=True)
    
    @api.multi
    def _compute_amounts(self):
        total_amount_subscribed = 0
        total_amount_transfered = 0
        total_amount_resold = 0
        for certificate in self:
            for line in certificate.subscribed_lines:
                total_amount_subscribed += line.amount_subscribed
            certificate.total_amount_subscribed = total_amount_subscribed
            
            for line in certificate.transfered_lines:
                total_amount_transfered += line.amount_transfered
            certificate.total_amount_transfered = total_amount_transfered
            
            for line in certificate.resold_lines:
                total_amount_resold += line.amount_resold
            certificate.total_amount_resold = total_amount_resold
            certificate.total_amount = certificate.total_amount_subscribed + certificate.total_amount_resold + certificate.total_amount_transfered
                     
    @api.multi
    def _compute_certificate_lines(self):
        for certificate in self:
            certificate.subscribed_lines = certificate.lines.filtered(lambda r: r.type == 'subscribed')
            certificate.resold_lines = certificate.lines.filtered(lambda r: r.type == 'resold')
            certificate.transfered_lines = certificate.lines.filtered(lambda r: r.type == 'transfered')
    
class TaxShelterCertificateLine(models.Model):
    _name="certificate.line"
    
    tax_shelter_certificate = fields.Many2one('tax.shelter.certificate', string="Tax shelter certificate",ondelete='cascade',required=True)
    share_type = fields.Many2one('product.product', string='Share type', required=True, readonly=True)
    share_unit_price = fields.Float(string='Share price', required=True, readonly=True)
    quantity = fields.Integer(string='Number of shares', required=True, readonly=True)
    transaction_date = fields.Date(string="Transaction date")
    type = fields.Selection([('subscribed','Subscribed'),
                             ('resold','Resold'),
                             ('transfered','Transfered'),
                             ('kept','Kept')], required=True, readonly=True) 
    amount_subscribed = fields.Float(compute='_compute_totals', string='Amount subscribed',store=True)
    amount_resold = fields.Float(compute='_compute_totals', string='Amount resold',store=True)
    amount_transfered = fields.Float(compute='_compute_totals', string='Amount transfered',store=True)
    share_short_name = fields.Char(string='Share type name', readonly=True)
    
    @api.multi
    @api.depends('quantity','share_unit_price')
    def _compute_totals(self):
        for line in self:
            if line.type == 'subscribed':
                line.amount_subscribed = line.share_unit_price * line.quantity
            if line.type == 'resold':
                line.amount_resold = line.share_unit_price * -(line.quantity)
            if line.type == 'transfered':
                line.amount_transfered = line.share_unit_price * -(line.quantity)
            