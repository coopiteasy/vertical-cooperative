from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    referral_source_id = fields.Many2one(
        comodel_name="referral.source",
        string="How did you hear about us?",
    )

    def get_partner_company_vals(self):
        partner_vals = super().get_partner_company_vals()
        partner_vals["referral_source_id"] = self.referral_source_id.id
        return partner_vals

    def get_partner_vals(self):
        partner_vals = super().get_partner_vals()
        partner_vals["referral_source_id"] = self.referral_source_id.id
        return partner_vals

    def get_representative_vals(self):
        contact_vals = super().get_representative_vals()
        contact_vals["referral_source_id"] = self.referral_source_id.id
        return contact_vals

    def get_person_info(self, partner):
        super().get_person_info(partner)
        self.referral_source_id = partner.referral_source_id
