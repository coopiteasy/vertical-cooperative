from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    company_type = fields.Selection(
        selection_add=[
            ("ei", "Individual company"),
            ("snc", "Partnership"),
            ("sa", "Limited company (SA)"),
            ("sarl", "Limited liability company (Ltd)"),  # noqa
            ("sc", "Cooperative"),
            ("asso", "Association"),
            ("fond", "Foundation"),
            ("edp", "Company under public law"),
        ]
    )

    def get_required_field(self):
        req_fields = super(SubscriptionRequest, self).get_required_field()
        if "iban" in req_fields:
            req_fields.remove("iban")

        return req_fields

    def check_iban(self, iban):
        if iban:
            return super(SubscriptionRequest, self).check_iban(iban)
        return True
