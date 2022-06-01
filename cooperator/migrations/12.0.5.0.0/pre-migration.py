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
)


def migrate(cr, version):
    _logger.info("renaming xml_ids")
    openupgrade.rename_xmlids(cr, renamed_xml_ids)
