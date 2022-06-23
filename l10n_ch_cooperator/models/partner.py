from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    legal_form = fields.Selection(
        selection_add=[
            ("ei", "Individual company"),
            ("snc", "Partnership"),
            ("sa", "Limited company (SA)"),
            ("sarl", "Limited liability company (Ltd)"),
            ("sc", "Cooperative"),
            ("asso", "Association"),
            ("fond", "Foundation"),
            ("edp", "Company under public law"),
        ]
    )
