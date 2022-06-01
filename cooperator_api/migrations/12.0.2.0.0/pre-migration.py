import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.1.0.0")

renamed_xmlids = [
    (
        "cooperator_api.auth_api_key_manager_emc_demo",
        "cooperator_api.auth_api_key_manager_demo",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("changing 'emc_api' to 'cooperator_api'")
    openupgrade.logged_query(
        env.cr,
        "UPDATE subscription_request SET source = 'cooperator_api' WHERE "
        "source = 'emc_api'",
    )
    _logger.info("renaming xmlids")
    openupgrade.rename_xmlids(env.cr, renamed_xmlids)
