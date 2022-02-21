# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date

from .abstract_emc_adapter import AbstractEMCAdapter


class SubscriptionRequestAdapter(AbstractEMCAdapter):
    _model = "subscription.request"
    _service = "subscription-request"

    def search(self, date_from=None, date_to=None):
        url = self._get_url()

        params = {}
        if date_from:
            params.update({"date_from": Date.to_string(date_from)})
        if date_to:
            params.update({"date_to": Date.to_string(date_to)})

        sr_list = self.backend.http_get_content(url, params=params)
        return {
            "count": sr_list["count"],
            "rows": [self.to_write_values(row) for row in sr_list["rows"]],
        }

    def _map_product(self, api_dict):
        """maps the external product id found in the api dict
        to its bound internal product
        """
        ProductTemplateBinding = self.backend.env["emc.binding.product.template"]
        external_product_id = api_dict["share_product"]["id"]
        share_product_binding = ProductTemplateBinding.search_binding(
            self.backend, external_product_id
        )
        if not share_product_binding:
            raise UserError(
                _(
                    "No binding exists for share product %s. Please contact "
                    "system administrator "
                )
                % api_dict["share_product"]["name"]
            )
        return share_product_binding.internal_id.product_variant_id

    def _map_capital_release_requests(self, api_dict):
        """maps the external invoice ids found in the api dict
        to their bound internal invoices or creates a binding
        from the record invoice."""
        InvoiceBinding = self.backend.env["emc.binding.account.invoice"]
        crr_external_ids = api_dict.get("capital_release_request", [])
        crr_internal_ids = []
        for external_id in crr_external_ids:
            existing_binding = InvoiceBinding.search_binding(self.backend, external_id)
            if existing_binding:
                crr_internal_ids.append(existing_binding.internal_id)
            else:
                # The api cannot currently process multiple capital release
                #   requests per subscription request. It will take the
                #   first or raise
                crr = self.record.capital_release_request
                if not crr:
                    raise ValidationError(
                        _(
                            "No capital release invoice generated "
                            "subscription request of %s %s. \n "
                            "Please contact your system administrator."
                        )
                        % (self.record.lastname, self.record.firstname)
                    )
                if len(crr) > 1:
                    raise ValidationError(
                        _(
                            "Cannot process multiple capital release invoices "
                            "for subscription request of %s %s at this time. \n "
                            "Please contact your system administrator."
                        )
                        % (self.record.lastname, self.record.firstname)
                    )
                new_binding = InvoiceBinding.create(
                    {
                        "backend_id": self.backend.id,
                        "external_id": external_id,
                        "internal_id": crr.id,
                    }
                )
                crr_internal_ids.append(new_binding.internal_id)
        return crr_internal_ids

    def to_write_values(self, api_dict):
        Country = self.backend.env["res.country"]
        address = api_dict["address"]
        country = Country.search([("code", "=", address["country"])])
        product_product = self._map_product(api_dict)
        crr_internal_ids = self._map_capital_release_requests(api_dict)
        crr_tuples = [(4, id_, 0) for id_ in crr_internal_ids]

        external_id = api_dict["id"]
        writable_dict = {
            "email": api_dict["email"],
            "is_company": api_dict["is_company"],
            "firstname": api_dict["firstname"],
            "lastname": api_dict["lastname"],
            "date": api_dict["date"],
            "state": api_dict["state"],
            "lang": api_dict["lang"],
            "birthdate": api_dict["birthdate"],
            "gender": api_dict["gender"],
            "iban": api_dict["iban"],
            "phone": api_dict["phone"],
            "ordered_parts": api_dict["ordered_parts"],
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "share_product_id": product_product.id,
            "capital_release_request_date": api_dict["capital_release_request_date"],
            "data_policy_approved": api_dict["data_policy_approved"],
            "internal_rules_approved": api_dict["internal_rules_approved"],
            "financial_risk_approved": api_dict["financial_risk_approved"],
            "capital_release_request": crr_tuples,
            "skip_control_ng": api_dict["skip_control_ng"],
            "generic_rules_approved": api_dict["generic_rules_approved"],
            "source": "emc_api",
        }
        return external_id, writable_dict
