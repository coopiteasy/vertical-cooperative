from __future__ import division

from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp import api, fields, models


class DividendYear(models.Model):
    _name = "dividend.year"

    @api.multi
    def _compute_dividend_info(self):
        res = {}
        for dividend in self:
            res[dividend.id] = {
                "grand_total_dividend": 0.0,
                "grand_total_taxes": 0.0,
            }
            for line in dividend.dividend_ids:
                res[dividend.id][
                    "grand_total_dividend"
                ] += line.dividend_amount
                res[dividend.id]["grand_total_taxes"] += line.dividend_taxes
        return res

    name = fields.Char(string="Code")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    #     fiscal_year_id = fields.Many2one('account.fiscalyear',
    #                                      string='Fiscal year')
    percentage = fields.Float(string="Percentage")
    withholding_tax = fields.Float(string="Withholding tax")
    detailed_dividend_ids = fields.One2many(
        "detailed.dividend.line", "dividend_year_id", string="Dividend lines"
    )
    dividend_ids = fields.One2many(
        "dividend.line", "dividend_year_id", string="Dividend lines"
    )
    grand_total_dividend = fields.Float(
        compute=_compute_dividend_info,
        string="Grand total dividend",
        digits_compute=dp.get_precision("Account"),
    )
    grand_total_taxes = fields.Float(
        compute=_compute_dividend_info,
        string="Grand total taxes",
        digits_compute=dp.get_precision("Account"),
    )

    @api.multi
    def compute_dividend(self):
        self.ensure_one()
        det_div_line_obj = self.env["detailed.dividend.line"]
        div_line_obj = self.env["dividend.line"]
        res_partner_obj = self.env["res.partner"]

        # delete lines if any
        detailed_dividend_ids = det_div_line_obj.search(
            [("dividend_year_id", "=", self.id)]
        )
        detailed_dividend_ids.unlink()
        dividend_ids = div_line_obj.search(
            [("dividend_year_id", "=", self.id)]
        )
        dividend_ids.unlink()

        partner_ids = res_partner_obj.search(
            [("cooperator", "=", True), ("member", "=", True)],
            order="cooperator_register_number",
        )
        number_of_days = (
            datetime.strptime(self.date_to, "%Y-%m-%d")
            - datetime.strptime(self.date_from, "%Y-%m-%d")
        ).days + 1

        for partner in partner_ids:
            total_amount_dividend = 0.0
            for line in partner.share_ids:
                vals = {}
                vals2 = {}
                line_id = False
                if (
                    line.effective_date >= self.date_from
                    and line.effective_date <= self.date_to
                ):
                    date_res = (
                        datetime.strptime(self.date_to, "%Y-%m-%d")
                        - datetime.strptime(line.effective_date, "%Y-%m-%d")
                    ).days
                    coeff = (date_res / number_of_days) * self.percentage
                    dividend_amount = line.total_amount_line * coeff

                    vals["days"] = date_res
                    vals["dividend_year_id"] = self.id
                    vals[
                        "coop_number"
                    ] = line.partner_id.cooperator_register_number
                    vals["partner_id"] = partner.id
                    vals["share_line_id"] = line.id
                    vals["coeff"] = coeff
                    vals["dividend_amount"] = dividend_amount
                    total_amount_dividend += dividend_amount

                    line_id = det_div_line_obj.create(vals)
                elif line.effective_date < self.date_from:
                    dividend_amount = line.total_amount_line * self.percentage
                    vals["days"] = number_of_days
                    vals["dividend_year_id"] = self.id
                    vals[
                        "coop_number"
                    ] = line.partner_id.cooperator_register_number
                    vals["partner_id"] = partner.id
                    vals["share_line_id"] = line.id
                    vals["coeff"] = self.percentage
                    vals["dividend_amount"] = dividend_amount
                    total_amount_dividend += dividend_amount

                    line_id = det_div_line_obj.create(vals)
            if line_id:
                vals2[
                    "coop_number"
                ] = line.partner_id.cooperator_register_number
                vals2["dividend_year_id"] = self.id
                vals2["partner_id"] = line.partner_id.id

                vals2["dividend_amount_net"] = total_amount_dividend
                vals2["dividend_amount"] = total_amount_dividend

                # TODO set as a parameter on dividend year object
                if total_amount_dividend <= 190.00:
                    vals2["dividend_taxes"] = 0.0
                else:
                    div_tax = (
                        total_amount_dividend - 190
                    ) * self.withholding_tax
                    vals2["dividend_taxes"] = div_tax
                    vals2["dividend_amount_net"] = (
                        total_amount_dividend - div_tax
                    )

                div_line_obj.create(vals2)
        return True


class DetailedDividendLine(models.Model):
    _name = "detailed.dividend.line"

    @api.multi
    def _compute_total_line(self):
        res = {}
        for line in self:
            res[line.id] = line.share_unit_price * line.share_number
        return res

    dividend_year_id = fields.Many2one("dividend.year", string="Dividend year")
    coop_number = fields.Integer(string="Cooperator Number")
    days = fields.Integer(string="Days")
    partner_id = fields.Many2one(
        "res.partner", string="Cooperator", readonly=True
    )
    share_line_id = fields.Many2one(
        "share.line", string="Share line", readonly=True
    )
    share_number = fields.Integer(
        related="share_line_id.share_number", string="Number of Share"
    )
    share_unit_price = fields.Monetary(
        string="Share unit price", related="share_line_id.share_unit_price"
    )
    effective_date = fields.Date(
        related="share_line_id.effective_date", string="Effective date"
    )
    total_amount_line = fields.Monetary(
        string="Total value of share",
        currency_field="company_currency_id",
        compute=_compute_total_line,
        readonly=True,
    )
    coeff = fields.Float(string="Coefficient to apply", digits=(2, 4))
    dividend_amount = fields.Float(string="Gross Dividend")
    dividend_amount_net = fields.Float(string="Dividend net")
    dividend_taxes = fields.Float(string="Taxes")
    company_currency_id = fields.Many2one(
        related="share_line_id.company_currency_id", readonly=True
    )


class DividendLine(models.Model):
    _name = "dividend.line"

    @api.multi
    def _get_account_number(self):
        res = {}
        for line in self:
            bank_accounts = self.env["res.partner.bank"].search(
                [("partner_id", "=", line.partner_id.id)]
            )
            res[line.id] = bank_accounts[0].acc_number

        return res

    coop_number = fields.Integer(string="Coop Number")
    dividend_year_id = fields.Many2one("dividend.year", string="Dividend year")
    partner_id = fields.Many2one(
        "res.partner", string="Cooperator", readonly=True
    )
    account_number = fields.Char(
        compute=_get_account_number, string="Account Number"
    )
    dividend_amount = fields.Float(string="Gross Dividend")
    dividend_amount_net = fields.Float(string="Dividend net")
    dividend_taxes = fields.Float(string="Taxes")
