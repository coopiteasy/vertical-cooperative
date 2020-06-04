# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from os.path import join

from odoo import _
from odoo.exceptions import UserError
from odoo.fields import Date


class SubscriptionRequestAdapter:
    _model = "subscription.request"
    _root = "api"
    _service = "subscription-request"

    def __init__(self, backend):
        self.backend = backend

    def get_url(self, args):
        """args is a list of path elements
        :return the complete route to the service
        """
        return join("/", self._root, self._service, *args)

    def create(self):
        # pylint: disable=method-required-super
        raise NotImplementedError

    def search(self, date_from=None, date_to=None):
        url = self.get_url([])
        params = {}
        if date_from:
            params.update({"date_from": Date.to_string(date_from)})
        if date_to:
            params.update({"date_to": Date.to_string(date_to)})

        sr_list = self.backend.http_get_content(url, params=params)
        return sr_list

    def read(self, id_):
        # pylint: disable=method-required-super
        url = self.get_url([str(id_)])
        sr = self.backend.http_get_content(url)
        return sr

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def to_write_values(self, request):
        """
        :return a writable dictionary of values from the dictionary
        received from the api
        """
        Country = self.backend.env["res.country"]
        ProductTemplateBinding = self.backend.env[
            "emc.binding.product.template"
        ]
        address = request["address"]

        country = Country.search([("code", "=", address["country"])])

        external_product_id = request["share_product"]["id"]
        share_product_binding = ProductTemplateBinding.search_binding(
            self.backend, external_product_id
        )
        if not share_product_binding:
            raise UserError(
                _(
                    "No binding exists for share product %s. Please contact "
                    "system administrator "
                )
                % request["share_product"]["name"]
            )
        product_product = share_product_binding.internal_id.product_variant_id

        return {
            "email": request["email"],
            "name": request["name"],
            "date": request["date"],
            "state": request["state"],
            "lang": request["lang"],
            "ordered_parts": request["ordered_parts"],
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "share_product_id": product_product.id,
            "source": "emc_api",
        }
