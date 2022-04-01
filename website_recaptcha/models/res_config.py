# Copyright 2019 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PortalConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    recaptcha_key_site = fields.Char()
    recaptcha_key_secret = fields.Char()

    has_google_recaptcha = fields.Boolean(
        "Google reCaptcha",
        compute="_compute_has_google_recaptcha",
        inverse="_inverse_has_google_recaptcha",
        readonly=False,
    )
    # "?????"
    # @api.depends("website_id")
    # def _compute_has_google_recaptcha(self):
    #     self.has_google_recaptcha = bool(self.recaptcha_key_site)

    # def _inverse_has_google_recaptcha(self):
    #     if not self.has_google_recaptcha:
    #         self.recaptcha_key_site = False
    #         self.recaptcha_key_secret = False
