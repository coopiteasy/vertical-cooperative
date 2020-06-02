# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from os.path import join

from odoo import api, fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    external_id = fields.Integer(
        string="External ID", index=True, required=False
    )

    @api.multi
    def get_external_id(self):
        self.ensure_one()
        if not self.external_id:
            self.external_id = self.env["ir.sequence"].next_by_code(
                "subscription.request.external.id"
            )
        return self.external_id
