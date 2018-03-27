# -*- coding: utf-8 -*-
import base64
from datetime import datetime

from openerp import api, fields, models, _

TYPE_MAP = {
    'subscription':'subscribed',
    'transfer':'transfered',
    'sell_back':'resold'
}
REPORT_DIC = {'subscription':('easy_my_coop_taxshelter_report.tax_shelter_subscription_report','Tax Shelter Subscription'),
              'shares':('easy_my_coop_taxshelter_report.tax_shelter_shares_report','Tax Shelter Shares')}
class TaxShelterDeclaration(models.Model):
    _name = "tax.shelter.declaration"
    
    name = fields.Char(string='Declaration year', required=True)
    fiscal_year = fields.Char(String="Fiscal year", required=True)
    tax_shelter_certificates = fields.One2many('tax.shelter.certificate','declaration_id', string='Tax shelter certificates', readonly=True)
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    month_from = fields.Char(String='Month from', required=True)
    month_to = fields.Char(String='Month to', required=True)
    tax_shelter_percentage = fields.Selection([('30','30%'),
                                               ('45','45%')],
                                              string='Tax Shelter percentage', required=True)
    state = fields.Selection([('draft','Draft'),
                              ('computed','Computed'),
                              ('validated','Validated')], 
                              string='State',required=True, default="draft")
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                 change_default=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get())
    tax_shelter_capital_limit = fields.Float(string="Tax shelter capital limit", required=True) 
    previously_subscribed_capital = fields.Float(String="Capital previously subscribed", readonly=True)


    def _prepare_line(self, certificate, entry, ongoing_capital_sub):
        line_vals = {}
        line_vals['tax_shelter_certificate'] = certificate.id
        line_vals['share_type'] = entry.share_product_id.id
        line_vals['share_short_name'] = entry.share_short_name
        line_vals['share_unit_price'] = entry.share_unit_price
        line_vals['quantity'] = entry.quantity
        line_vals['transaction_date'] = entry.date
        line_vals['type'] = TYPE_MAP[entry.type]
        if entry.type == 'subscription':
            capital_after_sub = ongoing_capital_sub + entry.total_amount_line
            line_vals['capital_before_sub'] = ongoing_capital_sub
            line_vals['capital_after_sub'] = capital_after_sub
            line_vals['capital_limit'] = self.tax_shelter_capital_limit
            if ongoing_capital_sub <= self.tax_shelter_capital_limit:
                line_vals['tax_shelter'] = True
        return line_vals
    
    def _compute_certificates(self,entries,partner_certificate):
        ongoing_capital_sub = 0.0
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
            line_vals = self._prepare_line(certificate, entry, ongoing_capital_sub)
            certificate.write({'lines': [(0, 0, line_vals)]})

            #if entry.type == 'subscription' and entry.date >= self.date_from:
            ongoing_capital_sub += entry.total_amount_line

        return partner_certificate
    
    @api.one
    def compute_declaration(self):
        entries = self.env['subscription.register'].search([('partner_id.is_company','=',False),
                                                    ('date','<=',self.date_to),
                                                    ('type','in',['subscription','sell_back','transfer'])])
        
        subscriptions = entries.filtered((lambda r: r.type == 'subscription' and r.date < self.date_from))
        cap_prev_sub = 0.0
        for subscription in subscriptions:
            cap_prev_sub += subscription.total_amount_line
        
        self.previously_subscribed_capital = cap_prev_sub
        
        partner_certificate = {}
        
        partner_certificate = self._compute_certificates(entries, partner_certificate)
        
        self.state = 'computed'
        
    @api.one    
    def validate_declaration(self):
        self.tax_shelter_certificates.write({'state':'validated'})
        self.state = 'validated'
    
    @api.one
    def reset_declaration(self):
        if not self.state == 'validated':
            certificate_ids = self.tax_shelter_certificates.ids
            self.tax_shelter_certificates.unlink()
            self.state = 'draft'
        
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
    previously_subscribed_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Previously Subscribed lines', readonly=True)
    subscribed_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Shares subscribed', readonly=True)
    resold_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Shares resold', readonly=True)
    transfered_lines = fields.One2many(compute='_compute_certificate_lines', comodel_name='certificate.line', string='Shares transfered', readonly=True)
    total_amount_previously_subscribed = fields.Float(compute='_compute_amounts', string='Total previously subscribed')
    total_amount_subscribed = fields.Float(compute='_compute_amounts', string='Total subscribed')
    total_amount_eligible = fields.Float(compute='_compute_amounts', string='Total amount eligible To Tax shelter')
    total_amount_resold = fields.Float(compute='_compute_amounts', string='Total resold')
    total_amount_transfered = fields.Float(compute='_compute_amounts', string='Total transfered')
    total_amount = fields.Float(compute='_compute_amounts', string='Total', readonly=True)
    company_id = fields.Many2one(related="declaration_id.company_id", string="Company")
    
    def generate_pdf_report(self,report_type):
        report_action, name = REPORT_DIC[report_type]
        report = self.env['report'].get_pdf(self, report_action)
        report = base64.b64encode(report)
        report_name = self.partner_id.name + ' ' + name + ' ' + self.declaration_id.name + '.pdf'
        
        return (report_name, report)

    def generate_certificates_report(self):
        attachments = []
        if self.total_amount_eligible > 0:
            #if self.total_amount_resold == 0 and self.total_amount_transfered == 0: 
            attachments.append(self.generate_pdf_report('subscription'))
        if self.total_amount_previously_subscribed > 0:
            attachments.append(self.generate_pdf_report('shares'))
        #if self.total_amount_resold > 0 or self.total_amount_transfered > 0:
            # TODO 
        return attachments
    
    @api.one
    def send_certificates(self):
        attachments = self.generate_certificates_report()
        if len(attachments) > 0:
            confirmation_mail_template = self.env['mail.template'].search([('name', '=', 'Tax Shelter Certificate - Send By Email')])[0]
            confirmation_mail_template.send_mail_with_multiple_attachments(self.id, attachments,True)
        
    @api.multi
    def print_subscription_certificate(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'easy_my_coop_taxshelter_report.tax_shelter_subscription_report')
    
    @api.multi
    def print_shares_certificate(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'easy_my_coop_taxshelter_report.tax_shelter_shares_report')    
        
    @api.multi
    def _compute_amounts(self):
        
        for certificate in self:
            total_amount_previously_subscribed = 0
            total_amount_subscribed = 0
            total_amount_elligible = 0
            total_amount_transfered = 0
            total_amount_resold = 0
            
            for line in certificate.subscribed_lines:
                total_amount_subscribed += line.amount_subscribed
            certificate.total_amount_subscribed = total_amount_subscribed
            
            for line in certificate.subscribed_lines:
                    total_amount_elligible += line.amount_subscribed_eligible
            certificate.total_amount_eligible = total_amount_elligible

            for line in certificate.previously_subscribed_lines:
                total_amount_previously_subscribed += line.amount_subscribed
            certificate.total_amount_previously_subscribed = total_amount_previously_subscribed
            
            for line in certificate.transfered_lines:
                total_amount_transfered += line.amount_transfered
            certificate.total_amount_transfered = total_amount_transfered
            
            for line in certificate.resold_lines:
                total_amount_resold += line.amount_resold
            certificate.total_amount_resold = total_amount_resold
            certificate.total_amount = certificate.total_amount_previously_subscribed + certificate.total_amount_subscribed + certificate.total_amount_resold + certificate.total_amount_transfered
    
    @api.multi
    def _compute_certificate_lines(self):
        for certificate in self:
            certificate.previously_subscribed_lines = certificate.lines.filtered(lambda r: r.type == 'subscribed' and r.transaction_date < certificate.declaration_id.date_from)
            certificate.subscribed_lines = certificate.lines.filtered(lambda r: r.type == 'subscribed' and r.transaction_date >= certificate.declaration_id.date_from and r.transaction_date <= certificate.declaration_id.date_to)
            certificate.resold_lines = certificate.lines.filtered(lambda r: r.type == 'resold' and r.transaction_date >= certificate.declaration_id.date_from and r.transaction_date <= certificate.declaration_id.date_to)
            certificate.transfered_lines = certificate.lines.filtered(lambda r: r.type == 'transfered' and r.transaction_date >= certificate.declaration_id.date_from and r.transaction_date <= certificate.declaration_id.date_to)
    
    @api.model
    def batch_send_tax_shelter_certificate(self):
        certificates = self.search([('state','=','validated')],limit=80)
        for certificate in certificates:
            certificate.send_certificates()
            certificate.state = 'sent' 
            self.env.cr.commit()
            
class TaxShelterCertificateLine(models.Model):
    _name= "certificate.line"
    
    declaration_id = fields.Many2one(related='tax_shelter_certificate.declaration_id', string="Declaration")
    tax_shelter_certificate = fields.Many2one('tax.shelter.certificate', string="Tax shelter certificate", ondelete='cascade', required=True)
    share_type = fields.Many2one('product.product', string='Share type', required=True, readonly=True)
    share_unit_price = fields.Float(string='Share price', required=True, readonly=True)
    quantity = fields.Integer(string='Number of shares', required=True, readonly=True)
    transaction_date = fields.Date(string="Transaction date")
    tax_shelter = fields.Boolean(string="Tax shelter eligible", readonly=True)
    type = fields.Selection([('subscribed','Subscribed'),
                             ('resold','Resold'),
                             ('transfered','Transfered'),
                             ('kept','Kept')], required=True, readonly=True) 
    amount_subscribed = fields.Float(compute='_compute_totals', string='Amount subscribed',store=True)
    amount_subscribed_eligible = fields.Float(compute='_compute_totals', string='Amount subscribed eligible',store=True)
    amount_resold = fields.Float(compute='_compute_totals', string='Amount resold',store=True)
    amount_transfered = fields.Float(compute='_compute_totals', string='Amount transfered',store=True)
    share_short_name = fields.Char(string='Share type name', readonly=True)
    capital_before_sub = fields.Float(string="Capital before subscription", readonly=True)
    capital_after_sub = fields.Float(string="Capital after subscription", readonly=True)
    capital_limit = fields.Float(string="Capital limit", readonly=True)

    @api.multi
    @api.depends('quantity','share_unit_price')
    def _compute_totals(self):       
        for line in self:
            #limit = line.declaration_id.tax_shelter_capital_limit
            if line.type == 'subscribed':
                line.amount_subscribed = line.share_unit_price * line.quantity
            if line.type == 'subscribed' and line.tax_shelter:
                if line.capital_before_sub < line.capital_limit and line.capital_after_sub >= line.capital_limit:
                    line.amount_subscribed_eligible = line.capital_limit - line.capital_before_sub
                elif line.capital_before_sub < line.capital_limit and line.capital_after_sub <= line.capital_limit:
                    line.amount_subscribed_eligible = line.share_unit_price * line.quantity
                elif line.capital_before_sub >= line.capital_limit:
                    line.amount_subscribed_eligible = 0
            if line.type == 'resold':
                line.amount_resold = line.share_unit_price * -(line.quantity)
            if line.type == 'transfered':
                line.amount_transfered = line.share_unit_price * -(line.quantity)
            