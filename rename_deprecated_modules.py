# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# undefined name 'env'
env = env  # noqa: F821

# Comments are there to prevent merge conflicts. Put the dictionary entry UNDER
# the comment of the respective module.
renamed_modules = {
    "easy_my_coop": "cooperator",
    "easy_my_coop_api": "connector_api",
    "easy_my_coop_api_logs": "connector_api_logs",
    "easy_my_coop_be": "l10n_be_cooperator",
    "easy_my_coop_ch": "l10n_ch_cooperator",
    # easy_my_coop_connector        => waiting for financité
    # easy_my_coop_dividend         => do not move to oca, not installable
    "easy_my_coop_es": "l10n_es_cooperator",
    "easy_my_coop_es_website": "l10n_es_cooperator",
    # easy_my_coop_export_xlsx      => do not move to oca, not installable
    "easy_my_coop_fr": "l10n_fr_cooperator",
    # easy_my_coop_loan             => do not move to oca, seldom used
    # easy_my_coop_loan_account     => idem
    # easy_my_coop_loan_account_be  => idem
    # easy_my_coop_loan_bba         => idem
    # easy_my_coop_loan_website     => idem
    "easy_my_coop_payment_term": "cooperator",
    "easy_my_coop_taxshelter_report": "l10n_be_cooperator",
    # easy_my_coop_website
    "easy_my_coop_website": "cooperator_website",
    "easy_my_coop_website_portal": "cooperator_portal",
    "easy_my_coop_website_taxshelter": "l10n_be_cooperator_portal",
    # partner_age                   => dependency removed, move to addons
    # theme_light                   => removed from dependencies
    "website_recaptcha_reloaded": "portal_recaptcha",  # => moved to addons
}

_logger.info("rename easy_my_coop_x modules to cooperator_x")
openupgrade.update_module_names(env.cr, renamed_modules.items(), merge_modules=True)
env.cr.commit()

modules_to_uninstall = [
    "partner_age",
]
for module in modules_to_uninstall:
    _logger.info("uninstall %s" % module)
    env["ir.module.module"].search([("name", "=", module)]).button_immediate_uninstall()
