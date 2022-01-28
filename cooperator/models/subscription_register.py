# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


@api.model
def _lang_get(self):
    languages = self.env["res.lang"].search([])
    return [(language.code, language.name) for language in languages]


class SubscriptionRegister(models.Model):
    _name = "subscription.register"
    _description = "Subscription register"

    @api.multi
    def _compute_total_line(self):
        for line in self:
            line.total_amount_line = line.share_unit_price * line.quantity

    name = fields.Char(string="Number Operation", required=True, readonly=True)
    register_number_operation = fields.Integer(
        string="Register Number Operation", required=True, readonly=True
    )
    partner_id = fields.Many2one(
        "res.partner", string="Cooperator", required=True, readonly=True
    )
    partner_id_to = fields.Many2one(
        "res.partner", string="Transfered to", readonly=True
    )
    date = fields.Date(string="Subscription Date", required=True, readonly=True)
    quantity = fields.Integer(string="Number of share", readonly=True)
    share_unit_price = fields.Monetary(
        string="Share price",
        currency_field="company_currency_id",
        readonly=True,
    )
    total_amount_line = fields.Monetary(
        string="Total amount line",
        currency_field="company_currency_id",
        compute="_compute_total_line",
    )
    share_product_id = fields.Many2one(
        "product.product",
        string="Share type",
        required=True,
        readonly=True,
        domain=[("is_share", "=", True)],
    )
    share_short_name = fields.Char(
        related="share_product_id.short_name",
        string="Share type name",
        readonly=True,
    )
    share_to_product_id = fields.Many2one(
        "product.product",
        string="Share to type",
        readonly=True,
        domain=[("is_share", "=", True)],
    )
    share_to_short_name = fields.Char(
        related="share_to_product_id.short_name",
        string="Share to type name",
        readonly=True,
    )
    quantity_to = fields.Integer(string="Number of share to", readonly=True)
    share_to_unit_price = fields.Monetary(
        string="Share to price",
        currency_field="company_currency_id",
        readonly=True,
    )
    type = fields.Selection(
        [
            ("subscription", "Subscription"),
            ("transfer", "Transfer"),
            ("sell_back", "Sell Back"),
            ("convert", "Conversion"),
        ],
        string="Operation Type",
        readonly=True,
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
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        readonly=True,
        default=lambda self: self.env.user,
    )

    _order = "register_number_operation asc"

    @api.model
    def read_group(
        self,
        domain,
        fields,
        groupby,
        offset=0,
        limit=None,
        orderby=False,
        lazy=True,
    ):
        if "share_unit_price" in fields:
            fields.remove("share_unit_price")
        if "register_number_operation" in fields:
            fields.remove("register_number_operation")
        res = super(SubscriptionRegister, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        if "total_amount_line" in fields:
            for line in res:
                if "__domain" in line:
                    lines = self.search(line["__domain"])
                    inv_value = 0.0
                    for line2 in lines:
                        inv_value += line2.total_amount_line
                    line["total_amount_line"] = inv_value
        return res
