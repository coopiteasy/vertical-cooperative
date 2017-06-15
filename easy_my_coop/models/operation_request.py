# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import api, fields, models, _
from openerp.addons.base_iban import base_iban
from openerp.exceptions import UserError, ValidationError

class operation_request(models.Model):
    _name = 'operation.request'
     
    def get_date_now(self):
        return datetime.strftime(datetime.now(), '%Y-%m-%d')
    
    @api.multi
    @api.depends('share_product_id', 'share_product_id.list_price','quantity')
    def _compute_subscription_amount(self):
        for operation_request in self:
            operation_request.subscription_amount = operation_request.share_product_id.list_price * operation_request.quantity
     
    request_date = fields.Date(string='Request date', default=lambda self: self.get_date_now())
    partner_id = fields.Many2one('res.partner', string='Cooperator', domain=[('member','=',True)],required=True)
    partner_id_to = fields.Many2one('res.partner',string='Transfered to', domain=[('cooperator','=',True)])
    operation_type = fields.Selection([('subscription','Subscription'),
                                       ('transfer','Transfer'),
                                       ('sell_back','Sell Back'),
                                       ('convert','Conversion')],string='Operation Type', required=True)
    share_product_id = fields.Many2one('product.product', string='Share type', domain=[('is_share','=',True)], required=True)
    share_product_id_to = fields.Many2one('product.product', string='Concert to this share type', domain=[('is_share','=',True)])
    share_short_name = fields.Char(related='share_product_id.short_name', string='Share type name')
    share_unit_price = fields.Float(related='share_product_id.list_price', string='Share price')
    subscription_amount = fields.Float(compute='_compute_subscription_amount', string='Subscription amount')
    quantity = fields.Integer(string='Number of share', required=True)
    state = fields.Selection([('draft','Draft'),
                              ('waiting','Waiting'),
                              ('approved','Approved'),
                              ('done','Done'),
                              ('cancelled','Cancelled'),
                              ('refused','Refused')], string='State',required=True, default='draft')
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True, default=lambda self: self.env.user)
    subscription_request = fields.One2many('subscription.request','operation_request_id', 
                                string="Share Receiver Info",
                                help="In case on a transfer of share. "
                                "If the share receiver isn't a effective member "
                                "then a subscription form should be filled.")
    receiver_not_member = fields.Boolean(string='Receiver is not a member')
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                 change_default=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get())
    
    invoice = fields.Many2one('account.invoice', string="Invoice")
     
    @api.one
    def approve_operation(self):
        self.write({'state':'approved'})
    
    @api.one
    def refuse_operation(self):
        self.write({'state':'refused'})
    
    @api.one
    def submit_operation(self):
        self.write({'state':'waiting'})
        
    @api.one
    def cancel_operation(self):
        self.write({'state':'cancelled'})
    
    @api.one
    def reset_to_draft(self):
        self.write({'state':'draft'})
    
    def get_total_share_dic(self, partner):
        total_share_dic = {}
        share_products = self.env['product.template'].search([('is_share','=',True)])
        
        for share_product in share_products:
            total_share_dic[share_product.id] = 0
            
        for line in partner.share_ids:
            total_share_dic[line.share_product_id.id] += line.share_number
        
        return total_share_dic
    
    # This function doesn't handle the case of a cooperator can own 
    # different kinds of share type
    def hand_share_over(self, partner, share_product_id, quantity):
        if not partner.member:
            raise ValidationError(_("This operation can't be executed if the cooperator is not an effective member"))
        
        share_ind = len(partner.share_ids)
        i = 1
        while quantity > 0:
            line = self.partner_id.share_ids[share_ind-i]
            if line.share_product_id.id == share_product_id.id:
                if quantity > line.share_number:
                    quantity -= line.share_number
                    line.unlink()
                else:
                    share_left = line.share_number - quantity
                    quantity = 0
                    line.write({'share_number': share_left})
            i += 1
        # if the cooperator sold all his shares he's no more an effective member
        remaning_share_dict = 0
        for share_quant in self.get_total_share_dic(partner).values():
            remaning_share_dict += share_quant
        if remaning_share_dict == 0:
            self.partner_id.write({'member': False,'old_member':True})
    
    def has_share_type(self):
        for line in self.partner_id.share_ids:
            if line.share_product_id.id == self.share_product_id.id:
                return True
        return False
    
    @api.one     
    def execute_operation(self):
        effective_date = self.get_date_now()
        
        if not self.has_share_type():
            raise ValidationError(_("The cooperator doesn't own this share type. Please choose the appropriate share type."))
        if self.state != 'approved':
            raise ValidationError(_("This operation must be approved before to be executed"))
        
        if self.operation_type in ['sell_back','convert','transfer']:
            total_share_dic = self.get_total_share_dic(self.partner_id)
        
            if self.quantity > total_share_dic[self.share_product_id.id]:
                raise ValidationError(_("The cooperator can't hand over more shares that he/she owns."))
        
        if self.operation_type == 'sell_back': 
            self.hand_share_over(self.partner_id, self.share_product_id, self.quantity)
        elif self.operation_type == 'convert':
            print "convert"
            amount_to_convert = self.share_unit_price * self.quantity
            share_to_quant = int(amount_to_convert / self.share_product_id_to.list_price)
            remainder = amount_to_convert % self.share_product_id_to.list_price 
            print self.share_product_id_to.list_price
            print amount_to_convert
            print share_to_quant
            print remainder
            #self.hand_share_over(self.partner_id, self.share_product_id, self.quantity)
        elif self.operation_type == 'transfer':
            if self.receiver_not_member:
                partner = self.subscription_request.create_coop_partner()
                #get cooperator number
                sequence_id = self.env['ir.sequence'].search([('name','=','Subscription Register')])[0]
                sub_reg_num = sequence_id.next_by_id()
                partner_vals = self.env['subscription.request'].get_eater_vals(partner, self.share_product_id)
                partner_vals['member'] = True
                partner_vals['cooperator_register_number'] = int(sub_reg_num)
                partner.write(partner_vals)
                self.partner_id_to = partner 
            else:
                if self.company_id.unmix_share_type and (self.partner_id_to.cooperator_type and self.partner_id.cooperator_type != self.partner_id_to.cooperator_type):
                   raise ValidationError(_("This share type could not be transfered "
                                           "to " + self.partner_id_to.name))
                if not self.partner_id_to.member:
                    partner_vals = self.env['subscription.request'].get_eater_vals(self.partner_id_to, self.share_product_id)
                    partner_vals['member'] = True
                    partner_vals['old_member'] = False
                    self.partner_id_to.write(partner_vals)
            #remove the parts to the giver
            self.hand_share_over(self.partner_id, self.share_product_id, self.quantity)
            #give the share to the receiver
            self.env['share.line'].create({'share_number':self.quantity,
                                       'partner_id':self.partner_id_to.id,
                                       'share_product_id':self.share_product_id.id,
                                       'share_unit_price':self.share_unit_price,
                                       'effective_date':effective_date})   
        else:
            raise ValidationError(_("This operation is not yet implemented."))
        
        sequence_operation = self.env['ir.sequence'].search([('name','=','Register Operation')])[0]
        sub_reg_operation = sequence_operation.next_by_id()
        
        values = {'name':sub_reg_operation,'register_number_operation':int(sub_reg_operation),
                'partner_id':self.partner_id.id, 'quantity':self.quantity, 
                'share_product_id':self.share_product_id.id, 'type':self.operation_type,
                'share_unit_price': self.share_unit_price, 'date':effective_date,
                }
        
        self.write({'state':'done'})
        
        email_template_obj = self.env['mail.template']
        if self.operation_type == 'transfer':
            values['partner_id_to'] = self.partner_id_to.id
            certificat_email_template = email_template_obj.search([('name', '=', "Share transfer - Send By Email")])[0]
            certificat_email_template.send_mail(self.partner_id_to.id, False)

        self.env['subscription.register'].create(values)
        
        certificat_email_template = email_template_obj.search([('name', '=', "Share update - Send By Email")])[0]
        certificat_email_template.send_mail(self.partner_id.id, False)
     