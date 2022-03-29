import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.1.0.0")


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("changing 'emc_api' to 'connector_api'")
    openupgrade.logged_query(
        env.cr,
        "UPDATE subscription_request SET source = 'connector_api' WHERE "
        "source = 'emc_api'",
    )
