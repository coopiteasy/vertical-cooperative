# -*- coding: utf-8 -*-

from openerp import api, fields, models


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

    register_number = fields.Char(string="Register Number",
                                  required=True,
                                  default=_get_register_number)
    cooperator = fields.Many2one('res.partner',
                                 string="Cooperator",
                                 default=_get_partner)

    @api.multi
    def update(self):

        cooperator = self.cooperator
        coop_vals = {}

        if cooperator.is_company:
            coop_vals['company_register_number'] = self.register_number

        if coop_vals:
            cooperator.write(coop_vals)

        return True
