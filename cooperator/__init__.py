from . import models
from . import report
from . import wizard


from openupgradelib import openupgrade
from odoo import api, SUPERUSER_ID


def rename_xml_ids(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    renamed_group_xml_ids = (
        ("easy_my_coop.group_easy_my_coop_user", "cooperator.cooperator_group_user"),
        (
            "easy_my_coop.group_easy_my_coop_manager",
            "cooperator.cooperator_group_manager",
        ),
    )

    renamed_menu_xml_ids = (
        (
            "easy_my_coop.menu_main_easy_my_coop",
            "cooperator.menu_cooperator_main",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_main_subscription",
            "cooperator.menu_cooperator_main_subscription",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_subscription_request",
            "cooperator.menu_cooperator_subscription_request",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_cooperator_candidate",
            "cooperator.menu_cooperator_cooperator_candidate",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_subscription_register",
            "cooperator.menu_cooperator_subscription_register",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_operation_request",
            "cooperator.menu_cooperator_operation_request",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_main_coop",
            "cooperator.menu_cooperator_main_coop",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_cooperator",
            "cooperator.menu_cooperator_cooperator",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_company_representative",
            "cooperator.menu_cooperator_company_representative",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_main_reporting",
            "cooperator.menu_cooperator_main_reporting",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_config",
            "cooperator.menu_cooperator_config",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_share_product",
            "cooperator.menu_cooperator_share_product",
        ),
        (
            "easy_my_coop.menu_easy_my_coop_templates",
            "cooperator.menu_cooperator_templates",
        ),
    )

    renamed_view_xml_ids = (
        (
            "easy_my_coop.subscription_request_form",
            "cooperator.subscription_request_view_form",
        ),
        (
            "easy_my_coop.action_invoice_tree_coop",
            "cooperator.account_invoice_action",
        ),
        (
            "easy_my_coop.view_account_journal_form_coop",
            "cooperator.view_account_journal_form",
        ),
        (
            "easy_my_coop.view_account_bank_journal_form_coop",
            "cooperator.view_account_bank_journal_form",
        ),
        (
            "easy_my_coop.action_easy_my_coop_email_templates",
            "cooperator.mail_template_action",
        ),
        (
            "easy_my_coop.email_template_form_emh",
            "cooperator.email_template_form",
        ),
        (
            "easy_my_coop.product_template_share_form_view",
            "cooperator.product_template_form_view",
        ),
        (
            "easy_my_coop.share_product_filter",
            "cooperator.product_template_search_view",
        ),
        (
            "easy_my_coop.share_product_action",
            "cooperator.product_template_action",
        ),
        (
            "easy_my_coop.view_company_inherit_form2",
            "cooperator.view_company_form",
        ),
        (
            "easy_my_coop.view_partner_form_easy_my_coop",
            "cooperator.view_partner_form",
        ),
        (
            "easy_my_coop.view_partner_tree_easy_my_coop",
            "cooperator.view_partner_tree",
        ),
        (
            "easy_my_coop.view_res_partner_filter_coop",
            "cooperator.view_res_partner_filter",
        ),
    )

    renamed_template_xml_ids = [
        (
            "easy_my_coop.emc_external_layout_standard",
            "cooperator.external_layout_standard",
        )
    ]
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)

    openupgrade.rename_xmlids(env.cr, renamed_menu_xml_ids)

    openupgrade.rename_xmlids(env.cr, renamed_group_xml_ids)

    openupgrade.rename_xmlids(env.cr, renamed_template_xml_ids)

    openupgrade.rename_fields(
        env,
        [("mail.template", "mail_template", "easy_my_coop", "is_cooperator_template")],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "easy_my_coop.action_invoice_tree1_view1",
            "easy_my_coop.action_invoice_tree1_view2",
            "easy_my_coop.account.action_invoice_tree1",
            "easy_my_coop.account.action_invoice_refund_out_tree",
        ],
    )


def uninstall_previous_version(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # uninstall the previous version of the module
    module_ids = env["ir.module.module"].search(
        [("name", "=", "easy_my_coop"), ("state", "=", "installed")]
    )
    if module_ids:
        module_ids.button_uninstall()
