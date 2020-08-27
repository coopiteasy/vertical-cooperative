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


class AccountPaymentService(Component):
    _name = "account.payment.service"
    _inherit = "emc.rest.service"
    _usage = "payment"
    _description = """
        Account Payment Services
    """

    def create(self, **params):  # pylint: disable=method-required-super
        params = self._prepare_create(params)
        payment = self.env["account.payment"].create(params)
        payment.post()
        return self._to_dict(payment)

    def _prepare_create(self, params):
        """Prepare a writable dictionary of values"""
        journal = self.env["account.journal"].search(
            [("_api_external_id", "=", params["journal"])]
        )
        if not journal:
            raise wrapJsonException(
                NotFound(_("No journal %s on platform") % params["journal"])
            )

        invoice = self.env["account.invoice"].search(
            [("_api_external_id", "=", params["invoice"])]
        )
        if not invoice:
            raise wrapJsonException(
                NotFound(_("No invoice %s on platform") % params["invoice"])
            )

        payment_method_id = self.env["account.payment.method"].search(
            [
                ("code", "=", params["payment_method"]),
                ("payment_type", "=", params["payment_type"]),
            ]
        )
        if not payment_method_id:
            codes = (
                self.env["account.payment.method"].search([]).mapped("code")
            )
            raise wrapJsonException(
                NotFound(_("Payment method must be one of %s") % codes)
            )

        return {
            "payment_date": params["payment_date"],
            "amount": params["amount"],
            "payment_type": params["payment_type"],
            "communication": params["communication"],
            "invoice_ids": [(4, invoice.id, False)],
            "payment_method_id": payment_method_id.id,
            "journal_id": journal.id,
            "partner_type": "customer",
        }

    def _to_dict(self, payment):
        invoice = {
            "id": payment.invoice_ids.get_api_external_id(),
            "name": payment.invoice_ids.number,
        }
        return {
            "id": payment.get_api_external_id(),
            "journal": self._one_to_many_to_dict(payment.journal_id),
            "invoice": invoice,
            "payment_date": Date.to_string(payment.payment_date),
            "amount": payment.amount,
            "communication": payment.communication,
        }

    def _validator_create(self):
        return schemas.S_PAYMENT_CREATE

    def _validator_return_create(self):
        return schemas.S_PAYMENT_RETURN_GET
