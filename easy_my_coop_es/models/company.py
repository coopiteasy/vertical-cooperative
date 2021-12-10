from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    property_cooperator_account = fields.Many2one(
        domain=[
            ("deprecated", "=", False),
        ],
    )
