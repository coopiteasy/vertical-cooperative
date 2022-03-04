# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

import logging

from werkzeug.exceptions import BadRequest, NotFound

from odoo import _
from odoo.exceptions import ValidationError
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
        sr = self.env["subscription.request"].search([("_api_external_id", "=", _id)])
        if sr:
            return self._to_dict(sr)
        else:
            raise wrapJsonException(
                NotFound(_("No subscription request for id %s") % _id)
            )

    def search(self, date_from=None, date_to=None):
        _logger.info("search from {} to {}".format(date_from, date_to))

        domain = [("state", "=", "draft")]
        if date_from:
            date_from = Date.from_string(date_from)
            domain.append(("date", ">=", date_from))
        if date_to:
            date_to = Date.from_string(date_to)
            domain.append(("date", "<=", date_to))

        requests = self.env["subscription.request"].search(domain)

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
        state = params.pop("state", False)
        params = self._prepare_update(params)
        sr = self.env["subscription.request"].search([("_api_external_id", "=", _id)])
        if not sr:
            raise wrapJsonException(
                NotFound(_("No subscription request for id %s") % _id)
            )

        sr.sudo().write(params)
        if state:
            try:
                sr.update_state(state)
            except ValidationError as e:
                raise wrapJsonException(BadRequest(e.name))
        return self._to_dict(sr)

    def _to_dict(self, sr):
        sr.ensure_one()
        sr.timestamp_export()

        if sr.capital_release_request:
            invoice_ids = [
                invoice.get_api_external_id() for invoice in sr.capital_release_request
            ]
        else:
            invoice_ids = []

        share_product = sr.share_product_id.product_tmpl_id
        return {
            "id": sr.get_api_external_id(),
            "is_company": sr.is_company,
            "firstname": sr.firstname,
            "lastname": sr.lastname,
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
            "birthdate": self._or_none(Date.to_string(sr.birthdate)),
            "gender": self._or_none(sr.gender),
            "iban": self._or_none(sr.iban),
            "phone": self._or_none(sr.phone),
            "capital_release_request_date": self._or_none(
                Date.to_string(sr.capital_release_request_date)
            ),
            "capital_release_request": invoice_ids,
            "data_policy_approved": sr.data_policy_approved,
            "internal_rules_approved": sr.internal_rules_approved,
            "financial_risk_approved": sr.financial_risk_approved,
            "generic_rules_approved": sr.generic_rules_approved,
            "skip_control_ng": sr.skip_control_ng,
        }

    def _get_country(self, code):
        country = self.env["res.country"].search([("code", "=", code)])
        if country:
            return country
        else:
            raise wrapJsonException(BadRequest(_("No country for isocode %s") % code))

    def _get_share_product(self, external_id):
        product_template = self.env["product.template"].search(
            [("_api_external_id", "=", external_id)]
        )
        if product_template:
            return product_template.product_variant_id
        else:
            raise wrapJsonException(BadRequest(_("No share for id %s") % external_id))

    def _prepare_create(self, params):
        """Prepare a writable dictionary of values"""
        address = params["address"]
        country = self._get_country(address["country"])

        share_product_id = self._get_share_product(params["share_product"])

        return {
            "firstname": params["firstname"],
            "lastname": params["lastname"],
            "is_company": params["is_company"],
            "email": params["email"],
            "ordered_parts": params["ordered_parts"],
            "share_product_id": share_product_id.id,
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "lang": params["lang"],
            "data_policy_approved": params["data_policy_approved"],
            "internal_rules_approved": params["internal_rules_approved"],
            "financial_risk_approved": params["financial_risk_approved"],
            "generic_rules_approved": params["generic_rules_approved"],
            "birthdate": params.get("birthdate"),
            "gender": params.get("gender"),
            "iban": params.get("iban"),
            "phone": params.get("phone"),
            "skip_control_ng": params.get("skip_control_ng"),
            "capital_release_request_date": params.get("capital_release_request_date"),
            "source": "emc_api",
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
            share_product_id = self._get_share_product(params["share_product"]).id
        else:
            share_product_id = None

        params = {
            "is_company": params.get("is_company"),
            "firstname": params.get("firstname"),
            "lastname": params.get("lastname"),
            "email": params.get("email"),
            "ordered_parts": params.get("ordered_parts"),
            "share_product_id": share_product_id,
            "address": address.get("street"),
            "zip_code": address.get("zip_code"),
            "city": address.get("city"),
            "country_id": address.get("country"),
            "lang": params.get("lang"),
            "data_policy_approved": params.get("data_policy_approved"),
            "internal_rules_approved": params.get("internal_rules_approved"),
            "financial_risk_approved": params.get("financial_risk_approved"),
            "generic_rules_approved": params.get("generic_rules_approved"),
            "birthdate": params.get("birthdate"),
            "gender": params.get("gender"),
            "iban": params.get("iban"),
            "phone": params.get("phone"),
            "skip_control_ng": params.get("skip_control_ng"),
            "capital_release_request_date": params.get("capital_release_request_date"),
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
