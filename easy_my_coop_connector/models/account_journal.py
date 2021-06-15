# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    binding_id = fields.One2many(
        comodel_name="emc.binding.account.journal",
        inverse_name="internal_id",
        string="Binding ID",
        required=False,
    )
