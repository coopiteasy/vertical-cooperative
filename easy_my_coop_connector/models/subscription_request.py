# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import date, timedelta

from odoo import api, fields, models

from ..components.emc_adapters import SubscriptionRequestAdapter

_logger = logging.getLogger(__name__)


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    source = fields.Selection(selection_add=[("emc_api", "Easy My Coop API")])
    binding_id = fields.One2many(
        comodel_name="emc.binding.subscription.request",
        inverse_name="internal_id",
        string="Binding ID",
        required=False,
    )

    @api.model
    def fetch_subscription_requests(self, date_from=None, date_to=None):
        SRBinding = self.env["emc.binding.subscription.request"]

        backend = self.env["emc.backend"].get_backend()
        adapter = SubscriptionRequestAdapter(backend=backend)
        requests_dict = adapter.search(date_from=date_from, date_to=date_to)
        for external_id, request_dict in requests_dict["rows"]:
            sr_binding = SRBinding.search_binding(backend, external_id)
            if sr_binding:  # update request
                sr_binding.internal_id.write(request_dict)
            else:
                srequest = self.env["subscription.request"].create(
                    request_dict
                )
                SRBinding.create(
                    {
                        "backend_id": backend.id,
                        "external_id": external_id,
                        "internal_id": srequest.id,
                    }
                )
        external_ids = [
            external_id for external_id, _ in requests_dict["rows"]
        ]
        srequests = SRBinding.search(
            [
                ("backend_id", "=", backend.id),
                ("external_id", "in", external_ids),
            ]
        ).mapped("internal_id")
        return srequests

    @api.model
    def backend_read(self, external_id):
        SRBinding = self.env["emc.binding.subscription.request"]

        backend = self.env["emc.backend"].get_backend()

        adapter = SubscriptionRequestAdapter(backend)
        _, request_values = adapter.read(external_id)
        sr_binding = SRBinding.search_binding(backend, external_id)

        if sr_binding:  # update request
            srequest = sr_binding.internal_id
            srequest.write(request_values)
        else:
            srequest = self.env["subscription.request"].create(request_values)
            SRBinding.create(
                {
                    "backend_id": backend.id,
                    "external_id": external_id,
                    "internal_id": srequest.id,
                }
            )
        return srequest

    @api.model
    def fetch_subscription_requests_cron(self):
        backend = self.env["emc.backend"].get_backend()

        date_to = date.today()
        date_from = date_to - timedelta(days=1)
        _logger.info(
            "fetching subscription requests at {backend} from {date_from} to "
            "{date_to}.".format(
                backend=backend.name, date_from=date_from, date_to=date_to
            )
        )
        self.fetch_subscription_requests(date_from=date_from, date_to=date_to)
        _logger.info("fetch done.")

    @api.multi
    def validate_subscription_request(self):
        self.ensure_one()
        invoice = super(
            SubscriptionRequest, self
        ).validate_subscription_request()

        if self.source == "emc_api":
            backend = self.env["emc.backend"].get_backend()
            sr_adapter = SubscriptionRequestAdapter(backend=backend)
            external_id, invoice_dict = sr_adapter.validate(
                self.binding_id.external_id
            )

            InvoiceBinding = self.env["emc.binding.account.invoice"]
            InvoiceBinding.create(
                {
                    "backend_id": backend.id,
                    "external_id": external_id,
                    "internal_id": invoice.id,
                }
            )

        return invoice
