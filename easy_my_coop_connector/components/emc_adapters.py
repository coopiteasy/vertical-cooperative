# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from urllib.parse import urljoin

from werkzeug.exceptions import BadRequest

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date


class AbstractEMCAdapter:
    _model = "set in implementation class"
    _root = "/api/"
    _service = "set in implementation class"

    def __init__(self, backend, record=None):
        self.backend = backend
        self.record = record

    def _get_url(self, args=None):
        """args is a list of path elements
        :return the complete route to the service
        """
        if args is None:
            args = []
        return urljoin(self._root, self._service, *args)

    def search(self, **params):
        raise NotImplementedError

    def read(self, id_):
        # pylint: disable=method-required-super
        url = self._get_url([str(id_)])
        api_dict = self.backend.http_get_content(url)
        return self.to_write_values(api_dict)

    def create(self, record):
        # pylint: disable=method-required-super
        url = self._get_url()
        api_dict = self.to_api_dict(record)
        external_record = self.backend.http_post_content(url, api_dict)
        external_id, writeable_dict = self.to_write_values(external_record)
        return external_id, writeable_dict

    def update(self, data):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def to_write_values(self, api_dict):
        """
        :return a tuple with
            - the external id
            - a writable dictionary for _model
        received from the api
        """
        raise NotImplementedError

    def to_api_dict(self, record):
        raise NotImplementedError


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

    def update(self, data):
        if self.record is None:
            raise AttributeError("record field must be set for an update.")
        external_id = self.record.binding_id.external_id
        url = "/".join((self._get_url(), str(external_id), "update"))
        try:
            request_dict = self.backend.http_post_content(url, data)
        except BadRequest as bad_request:
            raise ValidationError(
                _(
                    "The Synergie platform replied with this error message:"
                    "\n\n %s \n\n"
                    "Please contact your system administrator."
                )
            ) % bad_request.description
        return self.to_write_values(request_dict)

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
                            "subscription request %s. \n "
                            "Please contact your system administrator."
                        )
                        % self.record.name
                    )
                if len(crr) > 1:
                    raise ValidationError(
                        _(
                            "Cannot process multiple capital release invoices "
                            "for subscription request %s at this time. \n "
                            "Please contact your system administrator."
                        )
                        % self.record.name
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
            "name": api_dict["name"],
            "date": api_dict["date"],
            "state": api_dict["state"],
            "lang": api_dict["lang"],
            "ordered_parts": api_dict["ordered_parts"],
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "share_product_id": product_product.id,
            "source": "emc_api",
            "data_policy_approved": api_dict["data_policy_approved"],
            "internal_rules_approved": api_dict["internal_rules_approved"],
            "financial_risk_approved": api_dict["financial_risk_approved"],
            "capital_release_request": crr_tuples,
        }
        return external_id, writable_dict


class AccountInvoiceAdapter(AbstractEMCAdapter):
    _model = "account.invoice"
    _service = "invoice"

    def to_write_values(self, api_dict):
        external_id = api_dict.pop("id")
        writable_dict = api_dict
        return external_id, writable_dict


class AccountPaymentAdapter(AbstractEMCAdapter):
    _model = "account.payment"
    _service = "payment"

    def to_write_values(self, api_dict):
        api_dict = api_dict.copy()
        external_id = api_dict.pop("id")
        writable_dict = api_dict
        return external_id, writable_dict

    def to_api_dict(self, record):

        if not record.journal_id.binding_id:
            raise ValidationError(
                _(
                    "Journal %s is not bound to a journal on the platform. "
                    "Please contact system administrator."
                )
                % record.journal_id.name
            )

        if not record.invoice_ids.binding_id:
            raise ValidationError(
                _(
                    "Invoice %s is not bound to a journal on the platform. "
                    "Please contact system administrator."
                )
                % record.invoice_ids.name
            )

        return {
            "journal": record.journal_id.binding_id.external_id,
            "invoice": record.invoice_ids.binding_id.external_id,
            "payment_date": Date.to_string(record.payment_date),
            "amount": record.amount,
            "communication": record.communication,
            "payment_type": record.payment_type,
            "payment_method": record.payment_method_id.code,
        }
