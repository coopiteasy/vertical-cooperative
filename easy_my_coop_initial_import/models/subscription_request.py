from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    migrated_cooperator_register_number = fields.Integer(
        string="Migrated Cooperator Number"
    )
