# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError

class PartnerCreateSubscription(models.TransientModel):
    _name = "partner.create.subscription"
    _description = "Create Subscription From Partner"

    @api.multi
    @api.onchange('share_product')
    def on_change_share_type(self):
        self.share_qty = self.share_product.minimum_quantity
        
    @api.model
    def _default_product_id(self):
        domain = [('is_share','=',True),('default_share_product','=',True)]
        active_id = self.env.context.get('active_id')
        if active_id:
            partner = self.env['res.partner'].browse(active_id)
            if partner.is_company:
                domain.append(('by_company','=',True))
            else:
                domain.append(('by_individual','=',True))
        
        return self.env['product.product'].search(domain)[0]
    
    @api.model
    def _get_partner(self):
        active_id = self.env.context.get('active_id')
        return self.env['res.partner'].browse(active_id)
    
    @api.model
    def _get_is_company(self):
        return self._get_partner().is_company
            
    @api.model
    def _get_register_number(self):
        partner = self._get_partner()
        if partner.is_company:
            return partner.company_register_number
        else:
            return partner.national_register_number
                
    @api.model
    def _get_possible_share(self):
        domain = [('is_share','=',True)]
        partner = self._get_partner()
        if partner.is_company:
            domain.append(('by_company','=',True))
        else:
            domain.append(('by_individual','=',True))
    
        return domain
    
    @api.multi
    @api.depends('share_product', 'share_qty')
    def _compute_subscription_amount(self):
        for sub_request in self:
            sub_request.subscription_amount = sub_request.share_product.list_price * sub_request.share_qty
            
    is_company = fields.Boolean(String="Is company?", default=_get_is_company)
    cooperator = fields.Many2one('res.partner', string="Cooperator", default=_get_partner)
    register_number = fields.Char(string="Register Number", required=True, default=_get_register_number)
    share_product = fields.Many2one('product.product', string='Share Type', domain=lambda self: self._get_possible_share(),\
        default=_default_product_id, required=True)
    share_qty = fields.Integer(string="Share Quantity", required=True)
    share_unit_price = fields.Float(related='share_product.list_price', string='Share price', readonly=True)
    subscription_amount = fields.Float(compute='_compute_subscription_amount', string='Subscription amount', digits=dp.get_precision('Account'), readonly=True)
    
    @api.multi
    def create_subscription(self):
        sub_req = self.env['subscription.request']
        cooperator = self.cooperator
        vals = {'partner_id': cooperator.id,
                'share_product_id':self.share_product.id,
                'ordered_parts':self.share_qty,
                'user_id':self.env.uid,
                'source':'crm'}
        
        if self.is_company:
            vals['company_name'] = self.cooperator.name
            vals['company_register_number'] = self.register_number
            vals['is_company'] = True
        else:
            vals['name'] = self.cooperator.name
            vals['no_registre'] = self.register_number
        
        if not self._get_register_number():
            if self.is_company:
                cooperator.write({'company_register_number':self.register_number})
            else:
                if sub_req.check_belgian_identification_id(self.register_number):
                    cooperator.write({'national_register_number':self.register_number})
                else:
                    raise UserError(_("The national register number is not valid."))
                
        new_sub_req = sub_req.create(vals)
        #return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form, tree',
            'view_mode': 'form',
            'res_model': 'subscription.request',
            'res_id': new_sub_req.id,
            'target': 'current',
        }

