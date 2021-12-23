# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .abstract_emc_adapter import AbstractEMCAdapter


class AccountInvoiceAdapter(AbstractEMCAdapter):
    _model = "account.invoice"
    _service = "invoice"

    def to_write_values(self, api_dict):
        external_id = api_dict.pop("id")
        writable_dict = api_dict
        return external_id, writable_dict
