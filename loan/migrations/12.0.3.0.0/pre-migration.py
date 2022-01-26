import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

renamed_modules = {
    "easy_my_coop_loan": "loan",
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _logger.info("before pre-migration script")
    openupgrade.update_module_names(env.cr, renamed_modules.items())
    _logger.info("after pre-migration script")
