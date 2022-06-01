import logging

# for this major refactoring, we decided to depend on
# openupgradelib
from openupgradelib import openupgrade

from .menus import renamed_menu_xml_ids

_logger = logging.getLogger(__name__ + " 12.0.6.0.0")


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming xml_ids")
    openupgrade.rename_xmlids(env.cr, renamed_menu_xml_ids)
