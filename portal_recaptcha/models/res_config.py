# Copyright 2019 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PortalConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    recaptcha_key_site = fields.Char()
    recaptcha_key_secret = fields.Char()

    @api.model
    def get_values(self):
        res = super(PortalConfigSettings, self).get_values()
        res.update(
            recaptcha_key_site=self.env["ir.config_parameter"]
            .sudo()
            .get_param("portal_recaptcha.recaptcha_key_site"),
            recaptcha_key_secret=self.env["ir.config_parameter"]
            .sudo()
            .get_param("portal_recaptcha.recaptcha_key_secret"),
        )
        return res

    @api.multi
    def set_values(self):
        super(PortalConfigSettings, self).set_values()
        param = self.env["ir.config_parameter"].sudo()
        param.set_param("portal_recaptcha.recaptcha_key_site", self.recaptcha_key_site)
        param.set_param(
            "portal_recaptcha.recaptcha_key_secret", self.recaptcha_key_secret
        )
