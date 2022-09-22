from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    activate_referral_source = fields.Selection(
        [],
        "Activate field: 'How did you know about us?'",
    )
