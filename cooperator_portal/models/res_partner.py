# Copyright 2019 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        # Extremely awkward filter function.
        #
        # In `prepare_portal_layout_values()` of portal.py in our module, the
        # "iban" key is added to the values dict. Later in `account()` (where
        # the latter method is called upstream), we read the key and write its
        # value to the partner's res.partner.bank.
        #
        # However, in between those steps, the `account()` method in upstream
        # `portal` writes the entire values dict to res.partner (where we
        # currently are!). This is bad, because "iban" is not a field of
        # res.partner.
        #
        # So we just delete it here if it exists. It's naïve, and there must be
        # a better way, but the future developer who reads this comment can take
        # care of that.
        #
        # Note to future developer: `details_form_validate()` also does things
        # with an "iban" key. As far as I can tell, this is a completely
        # separate POST dictionary. This may save you some time.
        if "iban" in vals:
            del vals["iban"]
        return super().write(vals)
