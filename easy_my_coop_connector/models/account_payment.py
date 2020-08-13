# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..components.emc_adapters import AccountPaymentAdapter


class AccountPayment(models.Model):
    _inherit = "account.payment"

    binding_id = fields.One2many(
        comodel_name="emc.binding.account.payment",
        inverse_name="internal_id",
        string="Binding ID",
        required=False,
    )

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        for payment in self:
            if any(payment.invoice_ids.mapped("release_capital_request")):
                invoice_id = payment.invoice_ids
                if len(invoice_id) > 1:
                    raise ValidationError(
                        _(
                            "This version of easy my coop connector "
                            "can't handle several invoice per"
                            "payment. Please contact  your "
                            "system administrator"
                        )
                    )

                backend = self.env["emc.backend"].get_backend()
                adapter = AccountPaymentAdapter(backend=backend)
                external_id, external_record = adapter.create(payment)
                self.env["emc.binding.account.payment"].create(
                    {
                        "backend_id": backend.id,
                        "internal_id": payment.id,
                        "external_id": external_id,
                    }
                )

            return res
