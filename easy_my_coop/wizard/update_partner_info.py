# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError

class PartnerUpdateInfo(models.TransientModel):
    _name = "partner.update.info"
    _description = "Update Partner Info"

    @api.model
    def _get_partner(self):
        active_id = self.env.context.get('active_id')
        return self.env['res.partner'].browse(active_id)
    
    @api.model
    def _get_register_number(self):
        partner = self._get_partner()
        if partner.is_company:
            return partner.company_register_number
        else:
            return partner.national_register_number
    
    register_number = fields.Char(string="Register Number", required=True, default=_get_register_number)
    cooperator = fields.Many2one('res.partner', string="Cooperator", default=_get_partner)
    
    def check_belgian_ident_id(self, register_number):
        if self.env['subscription.request'].check_belgian_identification_id(register_number):
            return True
        else:
            raise UserError(_("The national register number is not valid."))

    @api.multi
    def update(self):
        
        cooperator = self.cooperator
        coop_vals = {}
        
        if self.is_company:
            coop_vals['company_register_number'] = self.register_number
        else:
            if self.check_belgian_ident_id(self.register_number):
                coop_vals['national_register_number'] = self.register_number
        
        if coop_vals:
            cooperator.write(coop_vals)

        return True
