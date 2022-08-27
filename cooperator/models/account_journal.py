# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    get_cooperator_payment = fields.Boolean("Get cooperator payments?")
    get_general_payment = fields.Boolean(string="Get general payments?")
