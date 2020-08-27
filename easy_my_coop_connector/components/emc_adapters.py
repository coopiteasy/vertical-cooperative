# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from os.path import join

from werkzeug.exceptions import BadRequest

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date


class AbstractEMCAdapter:
    _model = "set in implementation class"
    _root = "api"
    _service = "set in implementation class"

    def __init__(self, backend):
        self.backend = backend

    def _get_url(self, args=None):
        """args is a list of path elements
        :return the complete route to the service
        """
        if args is None:
            args = []
        return join("/", self._root, self._service, *args)

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

    def update(self):
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

    def validate(self, id_):
        url = self._get_url([str(id_), "validate"])
        data = {}
        try:
            invoice_dict = self.backend.http_post_content(url, data)
        except BadRequest as bad_request:
            raise ValidationError(
                _(
                    "The Synergie platform replied with this error message:"
                    "\n\n %s \n\n"
                    "Please contact your system administrator."
                )
                % bad_request.description
            )
        ai_adapter = AccountInvoiceAdapter(backend=self.backend)
        return ai_adapter.to_write_values(invoice_dict)

    def to_write_values(self, api_dict):
        Country = self.backend.env["res.country"]
        ProductTemplateBinding = self.backend.env[
            "emc.binding.product.template"
        ]
        address = api_dict["address"]

        country = Country.search([("code", "=", address["country"])])

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
        product_product = share_product_binding.internal_id.product_variant_id

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
