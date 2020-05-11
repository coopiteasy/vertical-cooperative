from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    legal_form = fields.Selection(
        selection_add=[
            ("asso", "Association"),
            ("eurl", "EURL / Entreprise individuelle"),
            ("sarl", "SARL"),
            ("sa", "SA / SAS"),
        ]
    )
