from odoo import api, fields, models

class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    def create_invoice(self, partner):
        invoice = super().create_invoice(partner)
        invoice.payment_term_id = self.env["res.company"]._company_default_get().default_payment_term
        return invoice
