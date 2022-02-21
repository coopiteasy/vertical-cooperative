# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.exceptions import ValidationError
from odoo.fields import Date

from .abstract_emc_adapter import AbstractEMCAdapter


class AccountPaymentAdapter(AbstractEMCAdapter):
    _model = "account.payment"
    _service = "payment"

    def to_write_values(self, api_dict):
        writable_dict = api_dict.copy()
        external_id = writable_dict.pop("id")
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
