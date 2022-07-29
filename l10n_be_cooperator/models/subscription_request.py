from odoo import models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    def get_company_type_selection(self):
        return [
            ("scrl", "SCRL"),
            ("asbl", "ASBL"),
            ("sprl", "SPRL"),
            ("sa", "SA"),
        ]
