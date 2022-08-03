# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

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
    share_to_product_id = fields.Many2one('product.product', string='Convert to this share type', domain=[('is_share','=',True)])
    share_short_name = fields.Char(related='share_product_id.short_name', string='Share type name')
    share_to_short_name = fields.Char(related='share_to_product_id.short_name', string='Share to type name')
    share_unit_price = fields.Float(related='share_product_id.list_price', string='Share price')
    share_to_unit_price = fields.Float(related='share_to_product_id.list_price', string='Share to price')
    subscription_amount = fields.Float(compute='_compute_subscription_amount', string='Operation amount')
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
     
    @api.multi
    def approve_operation(self):
        for rec in self:
            rec.write({'state':'approved'})
    
    @api.multi
    def refuse_operation(self):
        for rec in self:
            rec.write({'state':'refused'})
    
    @api.multi
    def submit_operation(self):
        for rec in self:
            rec.validate()
            rec.write({'state':'waiting'})
        
    @api.multi
    def cancel_operation(self):
        for rec in self:
            rec.write({'state':'cancelled'})
    
    @api.multi
    def reset_to_draft(self):
        for rec in self:
            rec.write({'state':'draft'})
    
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

    def validate(self):
        if not self.has_share_type() and self.operation_type in ['sell_back', 'transfer']:
            raise ValidationError(_("The cooperator doesn't own this share type. Please choose the appropriate share type."))
        
        if self.operation_type in ['sell_back','convert','transfer']:
            total_share_dic = self.get_total_share_dic(self.partner_id)
        
            if self.quantity > total_share_dic[self.share_product_id.id]:
                raise ValidationError(_("The cooperator can't hand over more shares that he/she owns."))
        
        if self.operation_type == 'convert' and self.company_id.unmix_share_type:
                if self.share_product_id.code == self.share_to_product_id.code:
                    raise ValidationError(_("You can't convert the share to the same share type."))
                if self.subscription_amount != self.partner_id.total_value :
                    raise ValidationError(_("You must convert all the shares to the selected type."))
        elif self.operation_type == 'transfer':
            if not self.receiver_not_member and self.company_id.unmix_share_type \
                and (self.partner_id_to.cooperator_type \
                     and self.partner_id.cooperator_type != self.partner_id_to.cooperator_type):
                   raise ValidationError(_("This share type could not be transfered "
                                           "to " + self.partner_id_to.name))
            
    @api.multi
    def execute_operation(self):
        effective_date = self.get_date_now()
        ir_sequence = self.env['ir.sequence']
        sub_request = self.env['subscription.request']
        email_template_obj = self.env['mail.template']
        
        
        for rec in self:
            rec.validate()

            if rec.state != 'approved':
                raise ValidationError(_("This operation must be approved before to be executed"))
            
            values = {
            'partner_id':rec.partner_id.id, 'quantity':rec.quantity, 
            'share_product_id':rec.share_product_id.id, 'type':rec.operation_type,
            'share_unit_price': rec.share_unit_price, 'date':effective_date,
            }
                        
            if rec.operation_type == 'sell_back': 
                self.hand_share_over(rec.partner_id, rec.share_product_id, rec.quantity)
            elif rec.operation_type == 'convert':
                amount_to_convert = rec.share_unit_price * rec.quantity
                convert_quant = int(amount_to_convert / rec.share_to_product_id.list_price)
                remainder = amount_to_convert % rec.share_to_product_id.list_price 
                
                if rec.company_id.unmix_share_type:
                    if convert_quant > 0 and remainder == 0:
                        share_ids = rec.partner_id.share_ids
                        line = share_ids[0]
                        if len(share_ids) > 1:
                            share_ids[1:len(share_ids)].unlink()
                        line.write({
                            'share_number':convert_quant,
                            'share_product_id':rec.share_to_product_id.id,
                            'share_unit_price': rec.share_to_unit_price,
                            'share_short_name': rec.share_to_short_name
                            })
                        values['share_to_product_id'] = rec.share_to_product_id.id
                        values['quantity_to'] = convert_quant
                else:
                    raise ValidationError(_("Converting just part of the shares is not yet implemented"))
            elif rec.operation_type == 'transfer':
                if rec.receiver_not_member:
                    partner = rec.subscription_request.create_coop_partner()
                    #get cooperator number
                    sequence_id = self.env.ref('easy_my_coop.sequence_subscription', False)
                    sub_reg_num = sequence_id.next_by_id()
                    partner_vals = sub_request.get_eater_vals(partner, rec.share_product_id)
                    partner_vals['member'] = True
                    partner_vals['cooperator_register_number'] = int(sub_reg_num)
                    partner.write(partner_vals)
                    rec.partner_id_to = partner 
                else:
                    if not rec.partner_id_to.member:
                        partner_vals = sub_request.get_eater_vals(rec.partner_id_to, rec.share_product_id)
                        partner_vals['member'] = True
                        partner_vals['old_member'] = False
                        rec.partner_id_to.write(partner_vals)
                #remove the parts to the giver
                self.hand_share_over(rec.partner_id, rec.share_product_id, rec.quantity)
                #give the share to the receiver
                self.env['share.line'].create({'share_number':rec.quantity,
                                           'partner_id':rec.partner_id_to.id,
                                           'share_product_id':rec.share_product_id.id,
                                           'share_unit_price':rec.share_unit_price,
                                           'effective_date':effective_date})
                values['partner_id_to'] = rec.partner_id_to.id
            else:
                raise ValidationError(_("This operation is not yet implemented."))
            
            #sequence_operation = ir_sequence.search([('name','=','Register Operation')])[0]
            sequence_operation = self.env.ref('easy_my_coop.sequence_register_operation', False)
            sub_reg_operation = sequence_operation.next_by_id()
            
            values['name'] = sub_reg_operation
            values['register_number_operation'] = int(sub_reg_operation)
            
            rec.write({'state':'done'})
            
            # send mail and to the receiver
            if rec.operation_type == 'transfer':
                certificat_email_template = self.env.ref('easy_my_coop.email_template_share_transfer', False)
                certificat_email_template.send_mail(rec.partner_id_to.id, False)
    
            self.env['subscription.register'].create(values)
            
            certificat_email_template = self.env.ref('easy_my_coop.email_template_share_update', False)
            certificat_email_template.send_mail(rec.partner_id.id, False)
     