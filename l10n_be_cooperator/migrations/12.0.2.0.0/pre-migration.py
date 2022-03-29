import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.2.0.0")

renamed_xmlids = [
    (
        "l10n_be_cooperator.menu_easy_my_coop_main_declaration",
        "l10n_be_cooperator.main_declaration_menu",
    ),
    (
        "l10n_be_cooperator.menu_tax_shelter_certificate",
        "l10n_be_cooperator.tax_shelter_certificate_menu",
    ),
    (
        "l10n_be_cooperator.menu_tax_shelter_declaration",
        "l10n_be_cooperator.tax_shelter_declaration_menu",
    ),
    (
        "l10n_be_cooperator.tax_shelter_certificate_form",
        "l10n_be_cooperator.tax_shelter_certificate_view_form",
    ),
    (
        "l10n_be_cooperator.tax_shelter_declaration_form",
        "l10n_be_cooperator.tax_shelter_declaration_view_form",
    ),
    (
        "l10n_be_cooperator.tax_shelter_declaration_tree",
        "l10n_be_cooperator.tax_shelter_declaration_view_tree",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming xmlids")
    openupgrade.rename_xmlids(env.cr, renamed_xmlids)
