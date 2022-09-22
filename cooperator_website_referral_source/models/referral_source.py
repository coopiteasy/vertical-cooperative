from odoo import fields, models


class ReferralSource(models.Model):
    _name = "referral.source"
    _description = "How did you know about us?"

    name = fields.Char("How did you know about us?")
