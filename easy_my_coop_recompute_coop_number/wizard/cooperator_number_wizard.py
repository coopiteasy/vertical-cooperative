# -*- coding: utf-8 -*-
from openerp import models, fields, api

class AddRespondentsWizard(models.TransientModel):
    _name = 'cooperator.number.wizard'
    
    from_number = fields.Integer(string="From number")
    to_number = fields.Integer(string="To number")
    reference = fields.Char(string="Reference", required=True, help='Enter your emails or references separeted by a semicolon')
    on_reference = fields.Boolean('On reference')
    on_email = fields.Boolean('On email', default=True)
    
    @api.onchange('on_reference')
    def onchange_reference(self):
        if self.on_reference:
            self.on_email = False
            
    @api.onchange('on_email')
    def onchange_email(self):    
        if self.on_email:
            self.on_reference = False
            
    @api.one
    def compute_cooperator_number(self):
        obj_sequence = self.env['ir.sequence']

        list = self.reference.split(',')

        for ref in list:
            coop = self.env['res.partner'].search([('cooperator','=',True),('member','=',True),('email','=',ref)])
            
            if coop:
                sequence_id = obj_sequence.search([('name','=','Subscription Register')])[0]
                sub_reg_num = sequence_id.next_by_id()
                coop.write({'cooperator_register_number':int(sub_reg_num)})
                
                subscription_register = self.env['subscription.register'].search([('partner_id','=',coop.id)])
                
                if subscription_register:
                    sequence_operation = obj_sequence.search([('name','=','Register Operation')])[0]
                    sub_reg_operation = sequence_operation.next_by_id()
                    
                    subscription_register.write({'name':sub_reg_operation,'register_number_operation':int(sub_reg_operation)})
                else:
                    print "subscription register not found for " + coop.name
                    
            else:
                print "cooperator not found for " + ref
        
