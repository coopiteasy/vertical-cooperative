from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    captcha_type = fields.Selection(
        [("none", "Disabled"), ("google", "Google Recaptcha")],
        "Captcha type or disabled",
        required=True,
        default="google",
    )
