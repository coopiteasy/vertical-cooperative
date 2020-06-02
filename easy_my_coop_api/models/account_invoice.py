# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    external_id = fields.Integer(
        string="External ID", index=True, required=False
    )

    @api.multi
    def get_external_id(self):
        self.ensure_one()
        if not self.external_id:
            self.external_id = self.env["ir.sequence"].next_by_code(
                "account.invoice.external.id"
            )
        return self.external_id
