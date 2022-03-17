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
    # easy_my_coop
    "easy_my_coop": "cooperator",
    # easy_my_coop_api_logs
    # easy_my_coop_be
    # easy_my_coop_ch
    # easy_my_coop_connector
    # easy_my_coop_dividend
    # easy_my_coop_es
    # easy_my_coop_es_website
    # easy_my_coop_export_xlsx
    # easy_my_coop_fr
    # easy_my_coop_loan
    # easy_my_coop_loan_account
    # easy_my_coop_loan_account_be
    # easy_my_coop_loan_bba
    # easy_my_coop_loan_website
    # easy_my_coop_payment_term
    # easy_my_coop_taxshelter_report
    # easy_my_coop_website
    # easy_my_coop_website_portal
    # easy_my_coop_website_taxshelter
    # partner_age
    # setup
    # theme_light
    # website_recaptcha_reloaded
}

_logger.info("rename easy_my_coop_x modules to cooperator_x")
openupgrade.update_module_names(env.cr, renamed_modules.items())
env.cr.commit()
