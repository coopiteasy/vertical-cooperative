# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited


from odoo.addons.component.core import Component

from . import schemas


class SubscriptionRequestService(Component):
    _inherit = "subscription.request.services"

    def _to_dict(self, sr):
        vals = super()._to_dict(sr)
        vals.update(
            {
                "vat": sr.vat,
            }
        )
        return vals

    def _prepare_create(self, params):
        """Prepare a writable dictionary of values"""
        create_vals = super()._prepare_create(params)
        create_vals["vat"] = params["vat"]
        return create_vals

    def _validator_create(self):
        validator = super()._validator_create()
        validator.update(schemas.S_SUBSCRIPTION_REQUEST_CREATE)
        return validator

    def _validator_return_create(self):
        validator = super()._validator_return_create()
        validator.update(schemas.S_SUBSCRIPTION_REQUEST_RETURN_GET)
        return validator
