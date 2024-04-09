# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["ir.config_parameter"].set_param(
        "partner_lastname_uppercase.convert_lastnames_to_uppercase", True
    )
