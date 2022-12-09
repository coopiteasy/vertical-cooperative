# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.cr.execute("select true from res_company where captcha_type = 'google'")
        recaptcha_enabled = bool(env.cr.fetchall())
        env["ir.config_parameter"].set_param(
            "portal_recaptcha.recaptcha_enabled", recaptcha_enabled
        )
