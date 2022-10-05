from odoo import fields, models


class ReferralSource(models.Model):
    _name = "referral.source"
    _description = "How did you hear about us?"

    name = fields.Char(string="How did you hear about us?", translate=True)
