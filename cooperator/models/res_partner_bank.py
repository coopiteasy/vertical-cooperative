# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    _sql_constraints = [
        ("unique_number", "Check(1=1)", "Account Number must be unique!")
    ]
