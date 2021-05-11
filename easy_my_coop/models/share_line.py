# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ShareLine(models.Model):
    _name = "share.line"
    _description = "Share line"

    @api.multi
    def _compute_total_line(self):
        res = {}
        for line in self:
            line.total_amount_line = line.share_unit_price * line.share_number
        return res

    share_product_id = fields.Many2one(
        "product.product", string="Share type", required=True, readonly=True
    )
    share_number = fields.Integer(
        string="Number of Share", required=True, readonly=True
    )
    share_short_name = fields.Char(
        related="share_product_id.short_name",
        string="Share type name",
        readonly=True,
    )
    share_unit_price = fields.Monetary(
        string="Share price",
        currency_field="company_currency_id",
        readonly=True,
    )
    effective_date = fields.Date(string="Effective Date", readonly=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Cooperator",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    total_amount_line = fields.Monetary(
        string="Total amount line",
        currency_field="company_currency_id",
        compute="_compute_total_line",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
    )
