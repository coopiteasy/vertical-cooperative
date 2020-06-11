# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

import logging

from werkzeug.exceptions import NotFound

from odoo import _
from odoo.fields import Date

from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class AccountInvoiceService(Component):
    _inherit = "base.rest.service"
    _name = "account.invoice.services"
    _usage = "invoice"
    _collection = "emc.services"
    _description = """
        Account Invoice Services
    """

    def get(self, _id):
        sr = self.env["account.invoice"].search(
            [("_api_external_id", "=", _id)]
        )
        if sr:
            return self._to_dict(sr)
        else:
            raise wrapJsonException(
                NotFound(_("No invoice found for id %s") % _id)
            )

    def _to_dict(self, invoice):
        invoice.ensure_one()

        if invoice.subscription_request:
            sr_external_id = invoice.subscription_request.get_api_external_id()
        else:
            sr_external_id = None

        # todo return dictionaries for Many2one fields
        data = {
            "id": invoice.get_api_external_id(),
            "name": invoice.name,
            "state": invoice.state,
            "type": invoice.type,
            "date": Date.to_string(invoice.date),
            "date_due": Date.to_string(invoice.date_due),
            "date_invoice": Date.to_string(invoice.date_invoice),
            "partner": invoice.partner_id.get_api_external_id(),
            "journal": invoice.journal_id.get_api_external_id(),
            "account": invoice.account_id.get_api_external_id(),
            "subscription_request": sr_external_id,
            "invoice_lines": [
                self._line_to_dict(line) for line in invoice.invoice_line_ids
            ],
        }
        return data

    def _line_to_dict(self, line):
        return {
            "name": line.name,
            "account": line.account_id.get_api_external_id(),
            "product": line.product_id.product_tmpl_id.get_api_external_id(),
            "quantity": line.quantity,
            "price_unit": line.price_unit,
        }

    def _validator_get(self):
        return schemas.S_INVOICE_GET

    def _validator_return_get(self):
        return schemas.S_INVOICE_RETURN_GET
