# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    binding_id = fields.One2many(
        comodel_name="emc.binding.account.invoice",
        inverse_name="internal_id",
        string="Binding ID",
        required=False,
    )
