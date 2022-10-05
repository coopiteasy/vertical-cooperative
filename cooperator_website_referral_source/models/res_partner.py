from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    referral_source_id = fields.Many2one(
        comodel_name="referral.source",
        string="How did you hear about us?",
    )
