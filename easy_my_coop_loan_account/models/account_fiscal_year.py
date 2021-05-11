# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountFiscalYear(models.Model):
    _inherit = "account.fiscal.year"

    @api.model
    def get_ongoing_fiscal_year(self, company_id=None):
        today = fields.Date.today()
        fy = self.env["account.fiscal.year"].search(
            [
                ("date_from", "<=", today),
                ("date_to", ">=", today),
            ]
        )

        if not fy:
            raise UserError(_("No fiscal year has been found for %s") % str(today))

        if company_id:
            return fy.filtered(lambda r: r.company_id == company_id)
        return fy

    @api.model
    def get_next_fiscal_year(self, date=None, company_id=None):
        if not date:
            date = fields.Date.today()
        nextyear = date + relativedelta(years=+1)
        fy = self.env["account.fiscal.year"].search(
            [
                ("date_from", "<=", nextyear),
                ("date_to", ">=", nextyear),
            ]
        )
        if not fy:
            raise UserError(
                _("No next fiscal year has been found for %s") % str(nextyear)
            )
        if company_id:
            return fy.filtered(lambda r: r.company_id == company_id)

        return fy
