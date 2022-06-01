import logging

# for this major refactoring, we decided to depend on
# openupgradelib
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.3.0.0")

renamed_xml_ids = (
    (
        "cooperator_portal.portal_my_details_emc",
        "cooperator_portal.portal_my_details",
    ),
    (
        "cooperator_portal.website_portal_details_form",
        "cooperator_portal.portal_layout",
    ),
)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming xml_ids")
    openupgrade.rename_xmlids(env.cr, renamed_xml_ids)
