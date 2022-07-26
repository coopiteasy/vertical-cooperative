from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    company_type = fields.Selection(
        [("scrl", "SCRL"), ("asbl", "ASBL"), ("sprl", "SPRL"), ("sa", "SA")]
    )

    def get_partner_company_vals(self):
        vals = super(SubscriptionRequest, self).get_partner_company_vals()
        vals["out_inv_comm_algorithm"] = "random"
        return vals

    def get_partner_vals(self):
        vals = super(SubscriptionRequest, self).get_partner_vals()
        # fixme out_inv_comm_type was removed from v12
        vals["out_inv_comm_type"] = "bba"
        vals["out_inv_comm_algorithm"] = "random"
        return vals

    def get_representative_valst(self):
        # fixme out_inv_comm_type was removed from v12
        vals = super(SubscriptionRequest, self).get_representative_vals()
        vals["out_inv_comm_type"] = "bba"
        vals["out_inv_comm_algorithm"] = "random"
        return vals
