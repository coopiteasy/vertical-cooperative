import logging

# for this major refactoring, we decided to depend on
# openupgradelib
from openupgradelib import openupgrade

from .groups import renamed_group_xml_ids
from .menus import renamed_menu_xml_ids
from .templates import renamed_template_xml_ids

_logger = logging.getLogger(__name__ + " 12.0.6.0.0")


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming menu xml_ids")
    openupgrade.rename_xmlids(env.cr, renamed_menu_xml_ids)

    _logger.info("renaming group xml_ids")
    openupgrade.rename_xmlids(env.cr, renamed_group_xml_ids)

    _logger.info("renaming template xml_ids")
    openupgrade.rename_xmlids(env.cr, renamed_template_xml_ids)

    _logger.info("renaming easy_my_coop field on mail.template")
    openupgrade.rename_fields(
        [("mail.template", "mail_template", "easy_my_coop", "is_cooperator_template")]
    )
