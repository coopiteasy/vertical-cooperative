# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from odoo.addons.component.core import Component
from odoo.addons.base_rest.http import wrapJsonException
from werkzeug.exceptions import NotFound, BadRequest
from odoo.fields import Date
from odoo import _
from . import schemas

_logger = logging.getLogger(__name__)


class SubscriptionRequestService(Component):
    _inherit = "base.rest.service"
    _name = "subscription.request.services"
    _usage = "subscription_request"  # service_name
    _collection = "emc.services"
    _description = """
    Subscription requests
    """

    def _to_dict(self, sr):
        sr.ensure_one()
        return {
            "id": sr.id,
            "name": sr.name,
            "email": sr.email,
            "date": Date.to_string(sr.date),
            "ordered_parts": sr.ordered_parts,
            "share_product": {
                "id": sr.share_product_id.id,
                "name": sr.share_product_id.name,
            },
            "address": {
                "street": sr.address,
                "zip_code": sr.zip_code,
                "city": sr.city,
                "country": sr.country_id.code,
            },
            "lang": sr.lang,
        }

    def _get_country(self, code):
        country = self.env["res.country"].search([("code", "=", code)])
        if country:
            return country
        else:
            raise wrapJsonException(
                BadRequest(_("No country for isocode %s") % code)
            )

    def _prepare_create(self, params):
        address = params["address"]
        country = self._get_country(address["country"])

        return {
            "name": params["name"],
            "email": params["email"],
            "ordered_parts": params["ordered_parts"],
            "share_product_id": params["share_product"],
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "lang": params["lang"],
        }

    def get(self, _id):
        # fixme remove sudo
        sr = self.env["subscription.request"].sudo().search([("id", "=", _id)])
        if sr:
            return self._to_dict(sr)
        else:
            raise wrapJsonException(
                NotFound(_("No subscription request for id %s") % _id)
            )

    def search(self, date_from=None, date_to=None):
        # fixme remove sudo
        _logger.info("search from %s to %s" % (date_from, date_to))

        domain = []
        if date_from:
            date_from = Date.from_string(date_from)
            domain.append(("date", ">=", date_from))
        if date_to:
            date_to = Date.from_string(date_to)
            domain.append(("date", "<=", date_to))

        requests = self.env["subscription.request"].sudo().search(domain)

        response = {
            "count": len(requests),
            "rows": [self._to_dict(sr) for sr in requests],
        }
        return response

    def create(self, **params):
        params = self._prepare_create(params)
        sr = self.env["subscription.request"].create(params)
        return self._to_dict(sr)

    def _validator_get(self):
        return {"_id": {"type": "integer"}}

    def _validator_return_get(self):
        return schemas.S_SUBSCRIPTION_REQUEST_GET

    def _validator_search(self):
        return {
            "date_from": {
                "type": "string",
                "check_with": schemas.date_validator,
            },
            "date_to": {
                "type": "string",
                "check_with": schemas.date_validator,
            },
        }

    def _validator_return_search(self):
        return schemas.S_SUBSCRIPTION_REQUEST_LIST

    def _validator_create(self):
        return schemas.S_SUBSCRIPTION_REQUEST_CREATE

    def _validator_return_create(self):
        return schemas.S_SUBSCRIPTION_REQUEST_GET
