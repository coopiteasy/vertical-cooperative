# Copyright 2021+ Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from calendar import monthrange


def _get_first_day_of_month(_):
    today = fields.Date.today()
    return today.replace(day=1)


def _get_last_day_of_month(_):
    today = fields.Date.today()
    _, days_in_month = monthrange(today.year, today.month)
    return today.replace(day=days_in_month)


class WithholdingTaxDeclarationWizard(models.Model):
    _name = "withholding.tax.declaration.wizard"
    _description = "Wizard to Compute Tax Withholding Declaration"

    date_start = fields.Date(
        string="Start Date",
        default=_get_first_day_of_month,
    )
    date_end = fields.Date(
        string="Date End",
        default=_get_last_day_of_month,
    )

    def action_export_pdf(self):
        self.ensure_one()
        return True
