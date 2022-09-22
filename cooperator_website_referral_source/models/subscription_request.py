from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    referral_source_id = fields.Many2one(
        comodel_name="referral.source",
        string="How did you know about us?",
    )
