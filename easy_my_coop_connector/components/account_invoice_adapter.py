# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .abstract_emc_adapter import AbstractEMCAdapter


class AccountInvoiceAdapter(AbstractEMCAdapter):
    _model = "account.invoice"
    _service = "invoice"

    def to_write_values(self, api_dict):
        writable_dict = api_dict.copy()
        external_id = writable_dict.pop("id")
        return external_id, writable_dict
