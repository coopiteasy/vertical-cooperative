from odoo import api,fields,models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    captcha_enabled = fields.Boolean("Google Recaptcha Module active?", default=True)

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
                'emc_website.captcha_enabled',
                'True' if self.captcha_enabled else 'False'
        )
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update({
            'captcha_enabled': (True if ICPSudo.get_param(
            'emc_website.captcha_enabled', default=True) == 'True' else False)
        })
        return res
