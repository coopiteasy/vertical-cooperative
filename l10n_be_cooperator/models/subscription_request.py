from odoo import fields, models

from . import partner


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    company_type = fields.Selection(selection_add=partner.get_company_type_selection())
