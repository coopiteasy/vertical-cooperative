# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_share = fields.Boolean(string="Is share?")
    short_name = fields.Char(string="Short name")
    display_on_website = fields.Boolean(string="Display on website")
    default_share_product = fields.Boolean(string="Default share product")
    minimum_quantity = fields.Integer(string="Minimum quantity", default=1)
    force_min_qty = fields.Boolean(string="Force minimum quantity?")
    by_company = fields.Boolean(string="Can be subscribed by companies?")
    by_individual = fields.Boolean(string="Can be subscribed by individuals?")
    # fixme belongs to cooperative supermarket domain
    customer = fields.Boolean(string="Become customer")
    mail_template = fields.Many2one("mail.template", string="Mail template")

    @api.multi
    def get_web_share_products(self, is_company):
        if is_company is True:
            product_templates = self.env["product.template"].search(
                [
                    ("is_share", "=", True),
                    ("display_on_website", "=", True),
                    ("by_company", "=", True),
                ]
            )
        else:
            product_templates = self.env["product.template"].search(
                [
                    ("is_share", "=", True),
                    ("display_on_website", "=", True),
                    ("by_individual", "=", True),
                ]
            )
        return product_templates
