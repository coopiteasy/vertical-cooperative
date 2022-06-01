# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SubscriptionRequest(models.Model):
    _name = "subscription.request"
    _inherit = ["subscription.request", "external.id.mixin"]

    source = fields.Selection(selection_add=[("emc_api", "Easy My Coop API")])

    @api.multi
    def update_state(self, state):
        self.ensure_one()
        # sudo is needed yo write on api type requests
        if state == "draft":
            self.sudo().unblock_subscription_request()
        elif state == "block":
            self.sudo().block_subscription_request()
        elif state == "done":
            self.sudo().validate_subscription_request()
        elif state == "waiting":
            self.sudo().put_on_waiting_list()
        elif state == "cancelled":
            self.sudo().cancel_subscription_request()
        elif state == "paid":
            raise ValidationError(
                _(
                    "Subscription are marked as paid through the capital "
                    "release request payments "
                )
            )
        else:
            raise ValidationError(_("Unknown state."))
