from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    imported_cooperator_register_number = fields.Integer(
        string="Imported Cooperator Number",
        help="""Cooperator Number imported from other system
        to use in the EMC initial import process. With this numbers Odoo sort
        the SubscriptionRequest to validate and mark as pay in order""",
    )
