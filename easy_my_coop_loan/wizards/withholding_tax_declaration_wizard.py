# Copyright 2021+ Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from calendar import monthrange


def _get_first_day_of_month(*args):
    today = fields.Date.today()
    return today.replace(day=1)


def _get_first_day_of_next_month(*args):
    first_day = _get_first_day_of_month()
    if first_day.month == 12:
        next_month = 1
    else:
        next_month = first_day.month + 1
    return first_day.replace(month=next_month)


class WithholdingTaxDeclarationWizard(models.Model):
    _name = "withholding.tax.declaration.wizard"
    _description = "Wizard to Compute Tax Withholding Declaration"

    date_start = fields.Date(
        string="Start Date",
        default=_get_first_day_of_month,
    )
    date_end = fields.Date(
        string="Date End",
        default=_get_first_day_of_next_month,
    )
    total_gross_interests = fields.Float(string="Total Gross Interests")
    total_withholding_tax = fields.Float(string="Total Withholding Tax")
    total_net_interests = fields.Float(string="Total Net Interests")

    def _compute_declaration_amounts(self):
        # Ces totaux concernent toutes les obligations
        # dont c’est l’anniversaire dans le mois courant, et qui sont
        # toujours en cours (aujourd’hui <= date de souscription + durée
        # de l’obligation).
        # todo notify: prit toujours en cours = date_end <= line.date_end
        #         #
        today = fields.Date.today()

        active_loans = self.env["loan.issue.line"].search(
            [
                ("date_end", "<=", self.date_end),
            ]
        )
        def filter_loans(l):
            current_year_loan = l.date.replace(year=today.year) == l.date
            birthday_loan = self.date_start <= l.date.replace(year=today.year) < self.date_end
            return birthday_loan and not current_year_loan

        declared_loans = active_loans.filtered(filter_loans)
        self.total_gross_interests = 2.0
        self.total_withholding_tax = 2.0
        self.total_net_interests = 2.0

    def action_export_pdf(self):
        self.ensure_one()
        self._compute_declaration_amounts()
        action = self.env.ref(
            "easy_my_coop_loan.action_withholding_tax_declaration_report"
        )
        context = dict(self.env.context)
        return action.with_context(context).report_action(self)
