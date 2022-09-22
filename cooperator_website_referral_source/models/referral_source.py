from odoo import fields, models


class ReferralSource(models.Model):
    _name = "referral.source"

    name = fields.Char("How did you know about us?")
