# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class EMCHistoryImportSR(models.TransientModel):
    _name = "emc.history.import.sr"
    _description = "emc.history.import.sr"

    def first_day_of_month(self):
        return date.today() - relativedelta(day=1)

    def last_day_of_month(self):
        return date.today() + relativedelta(day=31)

    name = fields.Char("Name", default="Import History")
    date_from = fields.Date(
        string="Date From", required=True, default=first_day_of_month
    )
    date_to = fields.Date(
        string="Date To", required=True, default=last_day_of_month
    )

    @api.multi
    def import_subscription_button(self):
        self.env["subscription.request"].fetch_subscription_requests(
            date_from=self.date_from, date_to=self.date_to
        )

        action = self.env.ref("easy_my_coop.subscription_request_action")
        return action.read()[0]
