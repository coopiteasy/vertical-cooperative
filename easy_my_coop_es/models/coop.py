from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    vat = fields.Char(
        string="Tax ID",
        help="""
        The Tax Identification Number. Complete it if the contact is subjected to
        government taxes. Used in some legal statements."
        """,
    )
    voluntary_contribution = fields.Monetary(
        string="Voluntary contribution",
        currency_field="company_currency_id",
        help="Voluntary contribution made by the cooperator while buying a share.",
    )

    def get_partner_vals(self):
        vals = super(SubscriptionRequest, self).get_partner_vals()
        vals["vat"] = self.vat
        return vals
