# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

import logging

from werkzeug.exceptions import BadRequest, NotFound

from odoo import _
from odoo.fields import Date

from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class SubscriptionRequestService(Component):
    _inherit = "emc.rest.service"
    _name = "subscription.request.services"
    _usage = "subscription-request"
    _description = """
        Subscription Request Services
    """

    def get(self, _id):
        sr = self.env["subscription.request"].search(
            [("_api_external_id", "=", _id)]
        )
        if sr:
            sr._timestamp_export()
            return self._to_dict(sr)
        else:
            raise wrapJsonException(
                NotFound(_("No subscription request for id %s") % _id)
            )

    def search(self, date_from=None, date_to=None):
        _logger.info("search from {} to {}".format(date_from, date_to))

        domain = []
        if date_from:
            date_from = Date.from_string(date_from)
            domain.append(("date", ">=", date_from))
        if date_to:
            date_to = Date.from_string(date_to)
            domain.append(("date", "<=", date_to))

        requests = self.env["subscription.request"].search(domain)
        requests._timestamp_export()

        response = {
            "count": len(requests),
            "rows": [self._to_dict(sr) for sr in requests],
        }
        return response

    def create(self, **params):  # pylint: disable=method-required-super

        params = self._prepare_create(params)
        sr = self.env["subscription.request"].create(params)
        return self._to_dict(sr)

    def update(self, _id, **params):
        params = self._prepare_update(params)
        sr = self.env["subscription.request"].search(
            [("_api_external_id", "=", _id)]
        )
        if not sr:
            raise wrapJsonException(
                NotFound(_("No subscription request for id %s") % _id)
            )
        sr.write(params)
        return self._to_dict(sr)

    def validate(self, _id, **params):
        sr = self.env["subscription.request"].search(
            [("_api_external_id", "=", _id)]
        )
        if not sr:
            raise wrapJsonException(
                NotFound(_("No subscription request for id %s") % _id)
            )
        if sr.state != "draft":
            raise wrapJsonException(
                BadRequest(
                    _("Subscription request %s is not in draft state") % _id
                )
            )
        invoice = sr.validate_subscription_request()
        invoice_service = self.work.component(usage="invoice")
        return invoice_service.get(invoice.get_api_external_id())

    def _to_dict(self, sr):
        sr.ensure_one()

        if sr.capital_release_request:
            invoice_ids = [
                invoice.get_api_external_id()
                for invoice in sr.capital_release_request
            ]
        else:
            invoice_ids = []

        share_product = sr.share_product_id.product_tmpl_id
        return {
            "id": sr.get_api_external_id(),
            "name": sr.name,
            "email": sr.email,
            "state": sr.state,
            "date": Date.to_string(sr.date),
            "ordered_parts": sr.ordered_parts,
            "share_product": self._one_to_many_to_dict(share_product),
            "address": {
                "street": sr.address,
                "zip_code": sr.zip_code,
                "city": sr.city,
                "country": sr.country_id.code,
            },
            "lang": sr.lang,
            "capital_release_request": invoice_ids,
        }

    def _get_country(self, code):
        country = self.env["res.country"].search([("code", "=", code)])
        if country:
            return country
        else:
            raise wrapJsonException(
                BadRequest(_("No country for isocode %s") % code)
            )

    def _get_share_product(self, template_id):
        product = self.env["product.product"].search(
            [("product_tmpl_id", "=", template_id)]
        )
        if product:
            return product
        else:
            raise wrapJsonException(
                BadRequest(_("No share for id %s") % template_id)
            )

    def _prepare_create(self, params):
        """Prepare a writable dictionary of values"""
        address = params["address"]
        country = self._get_country(address["country"])

        share_product_id = self._get_share_product(params["share_product"])

        return {
            "name": params["name"],
            "email": params["email"],
            "ordered_parts": params["ordered_parts"],
            "share_product_id": share_product_id.id,
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "lang": params["lang"],
        }

    def _prepare_update(self, params):
        if "address" in params:
            address = params["address"]
            if "country" in address:
                country = self._get_country(address["country"]).id
                address["country"] = country.id
        else:
            address = {}

        if "share_product" in params:
            share_product_id = self._get_share_product(
                params["share_product"]
            ).id
        else:
            share_product_id = None

        params = {
            "name": params.get("name"),
            "email": params.get("email"),
            "state": params.get("state"),
            "ordered_parts": params.get("ordered_parts"),
            "share_product_id": share_product_id,
            "address": address.get("street"),
            "zip_code": address.get("zip_code"),
            "city": address.get("city"),
            "country_id": address.get("country"),
            "lang": params.get("lang"),
        }
        params = {k: v for k, v in params.items() if v is not None}
        return params

    def _validator_get(self):
        return schemas.S_SUBSCRIPTION_REQUEST_GET

    def _validator_return_get(self):
        return schemas.S_SUBSCRIPTION_REQUEST_RETURN_GET

    def _validator_search(self):
        return schemas.S_SUBSCRIPTION_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_SUBSCRIPTION_REQUEST_RETURN_SEARCH

    def _validator_create(self):
        return schemas.S_SUBSCRIPTION_REQUEST_CREATE

    def _validator_return_create(self):
        return schemas.S_SUBSCRIPTION_REQUEST_RETURN_GET

    def _validator_update(self):
        return schemas.S_SUBSCRIPTION_REQUEST_UPDATE

    def _validator_return_update(self):
        return schemas.S_SUBSCRIPTION_REQUEST_RETURN_GET

    def _validator_validate(self):
        return schemas.S_SUBSCRIPTION_REQUEST_VALIDATE

    def _validator_return_validate(self):
        return schemas.S_INVOICE_RETURN_GET
