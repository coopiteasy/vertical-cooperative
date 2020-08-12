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
    _name = "account.invoice.service"
    _inherit = "emc.rest.service"
    _usage = "invoice"
    _description = """
        Account Invoice Services
    """

    def get(self, _id):
        ai = self.env["account.invoice"].search(
            [("_api_external_id", "=", _id)]
        )
        if ai:
            return self._to_dict(ai)
        else:
            raise wrapJsonException(
                NotFound(_("No invoice found for id %s") % _id)
            )

    def _to_dict(self, invoice):
        invoice.ensure_one()

        data = {
            "id": invoice.get_api_external_id(),
            "number": invoice.number,
            "state": invoice.state,
            "type": invoice.type,
            "date": Date.to_string(invoice.date),
            "date_due": Date.to_string(invoice.date_due),
            "date_invoice": Date.to_string(invoice.date_invoice),
            "partner": self._one_to_many_to_dict(invoice.partner_id),
            "journal": self._one_to_many_to_dict(invoice.journal_id),
            "account": self._one_to_many_to_dict(invoice.account_id),
            "subscription_request": self._one_to_many_to_dict(
                invoice.subscription_request
            ),
            "invoice_lines": [
                self._line_to_dict(line) for line in invoice.invoice_line_ids
            ],
        }
        return data

    def _line_to_dict(self, line):
        return {
            "name": line.name,
            "account": self._one_to_many_to_dict(line.account_id),
            "product": self._one_to_many_to_dict(
                line.product_id.product_tmpl_id
            ),
            "quantity": line.quantity,
            "price_unit": line.price_unit,
        }

    def _validator_get(self):
        return schemas.S_INVOICE_GET

    def _validator_return_get(self):
        return schemas.S_INVOICE_RETURN_GET
