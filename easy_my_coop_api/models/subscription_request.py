# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.fields import Datetime


class SubscriptionRequest(models.Model):
    _name = "subscription.request"
    _inherit = ["subscription.request", "external.id.mixin"]

    @api.multi
    def _timestamp_export(self):
        self.write({"last_api_export_date": Datetime.now()})
        self.filtered(lambda sr: not sr.first_api_export_date).write(
            {"first_api_export_date": Datetime.now()}
        )
