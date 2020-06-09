from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    legal_form = fields.Selection(
        selection_add=[
            ("scrl", "SCRL"),
            ("asbl", "ASBL"),
            ("sprl", "SPRL"),
            ("sa", "SA"),
        ]
    )
