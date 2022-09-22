from odoo.http import request

from odoo.addons.cooperator_website.controllers.main import WebsiteSubscription


class ReferralSourceWebsiteSubscription(WebsiteSubscription):
    def get_referral_sources(self):
        referral_sources = request.env["referral.source"].sudo().search([])
        return referral_sources

    def fill_values(self, values, is_company, logged, load_from_user=False):
        values = super().fill_values(values, is_company, logged, load_from_user)
        values["referral_sources"] = self.get_referral_sources()
        return values
