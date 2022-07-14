# Copyright 2019 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        # deleting iban because it is not a field in partner
        # it will be written afterwards to the partner's res.partner.bank
        # it is not deleted before because it needs to be validated
        # by details_form_validate()
        if "iban" in vals:
            del vals["iban"]
        res = super().write(vals)
        return res
