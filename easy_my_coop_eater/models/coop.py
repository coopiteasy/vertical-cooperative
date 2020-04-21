from odoo import api, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    def get_eater_vals(self, partner, share_product_id):
        vals = {}
        eater = share_product_id.eater

        if partner.is_company or partner.age < 18:
            eater = "eater"

        vals["eater"] = eater

        return vals

    @api.one
    def validate_subscription_request(self):

        invoice = super(
            SubscriptionRequest, self
        ).validate_subscription_request()[0]
        partner = invoice.partner_id

        vals = self.get_eater_vals(partner, self.share_product_id)
        partner.write(vals)

        return invoice
