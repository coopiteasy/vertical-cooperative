import logging

# for this major refactoring, we decided to depend on
# openupgradelib
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.5.0.0")

renamed_xml_ids = (
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
)


def migrate(cr, version):
    _logger.info("renaming xml_ids")
    openupgrade.rename_xmlids(cr, renamed_xml_ids)
