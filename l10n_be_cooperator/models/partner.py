from odoo import fields, models


def get_company_type_selection():
    return [
        ("scrl", "SCRL"),
        ("asbl", "ASBL"),
        ("sprl", "SPRL"),
        ("sa", "SA"),
    ]


class ResPartner(models.Model):
    _inherit = "res.partner"

    legal_form = fields.Selection(selection_add=get_company_type_selection())
