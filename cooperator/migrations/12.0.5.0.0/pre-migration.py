import logging

# for this major refactoring, we decided to depend on
# openupgradelib
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.5.0.0")

renamed_group_xml_ids = (
    ("cooperator.group_easy_my_coop_user", "cooperator.cooperator_group_user"),
    ("cooperator.group_easy_my_coop_manager", "cooperator.cooperator_group_manager"),
)

renamed_menu_xml_ids = (
    (
        "cooperator.menu_main_easy_my_coop",
        "cooperator.menu_cooperator_main",
    ),
    (
        "cooperator.menu_easy_my_coop_main_subscription",
        "cooperator.menu_cooperator_main_subscription",
    ),
    (
        "cooperator.menu_easy_my_coop_subscription_request",
        "cooperator.menu_cooperator_subscription_request",
    ),
    (
        "cooperator.menu_easy_my_coop_cooperator_candidate",
        "cooperator.menu_cooperator_cooperator_candidate",
    ),
    (
        "cooperator.menu_easy_my_coop_subscription_register",
        "cooperator.menu_cooperator_subscription_register",
    ),
    (
        "cooperator.menu_easy_my_coop_operation_request",
        "cooperator.menu_cooperator_operation_request",
    ),
    (
        "cooperator.menu_easy_my_coop_main_coop",
        "cooperator.menu_cooperator_main_coop",
    ),
    (
        "cooperator.menu_easy_my_coop_cooperator",
        "cooperator.menu_cooperator_cooperator",
    ),
    (
        "cooperator.menu_easy_my_coop_company_representative",
        "cooperator.menu_cooperator_company_representative",
    ),
    (
        "cooperator.menu_easy_my_coop_main_reporting",
        "cooperator.menu_cooperator_main_reporting",
    ),
    (
        "cooperator.menu_easy_my_coop_config",
        "cooperator.menu_cooperator_config",
    ),
    (
        "cooperator.menu_easy_my_coop_share_product",
        "cooperator.menu_cooperator_share_product",
    ),
    (
        "cooperator.menu_easy_my_coop_templates",
        "cooperator.menu_cooperator_templates",
    ),
)

renamed_view_xml_ids = (
    (
        "cooperator.subscription_request_form",
        "cooperator.subscription_request_view_form",
    ),
    (
        "cooperator.action_invoice_tree_coop",
        "cooperator.account_invoice_action",
    ),
    (
        "cooperator.view_account_journal_form_coop",
        "cooperator.view_account_journal_form",
    ),
    (
        "cooperator.view_account_bank_journal_form_coop",
        "cooperator.view_account_bank_journal_form",
    ),
    (
        "cooperator.action_easy_my_coop_email_templates",
        "cooperator.mail_template_action",
    ),
    (
        "cooperator.email_template_form_emh",
        "cooperator.email_template_form",
    ),
    (
        "cooperator.product_template_share_form_view",
        "cooperator.product_template_form_view",
    ),
    (
        "cooperator.share_product_filter",
        "cooperator.product_template_search_view",
    ),
    (
        "cooperator.share_product_action",
        "cooperator.product_template_action",
    ),
    (
        "cooperator.view_company_inherit_form2",
        "cooperator.view_company_form",
    ),
    (
        "cooperator.view_partner_form_easy_my_coop",
        "cooperator.view_partner_form",
    ),
    (
        "cooperator.view_partner_tree_easy_my_coop",
        "cooperator.view_partner_tree",
    ),
    (
        "cooperator.view_res_partner_filter_coop",
        "cooperator.view_res_partner_filter",
    ),
)

renamed_template_xml_ids = [
    ("cooperator.emc_external_layout_standard", "cooperator.external_layout_standard")
]


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming view xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)

    _logger.info("renaming menu xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_menu_xml_ids)

    _logger.info("renaming group xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_group_xml_ids)

    _logger.info("renaming template xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_template_xml_ids)

    _logger.info("renaming easy_my_coop field on mail.template")
    openupgrade.rename_fields(
        env,
        [("mail.template", "mail_template", "easy_my_coop", "is_cooperator_template")],
    )
