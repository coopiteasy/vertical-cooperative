import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.1.0.0")

renamed_models = [
    ("emc.api.log", "cooperator.api.log"),
]

renamed_tables = [
    ("emc_api_log", "cooperator_api_log"),
]

renamed_xmlids = [
    (
        "cooperator_api_logs.emc_api_log_view_form",
        "cooperator_api_logs.cooperator_api_log_view_form",
    ),
    (
        "cooperator_api_logs.emc_api_log_view_tree",
        "cooperator_api_logs.cooperator_api_log_view_tree",
    ),
    (
        "cooperator_api_logs.emc_api_log_action",
        "cooperator_api_logs.cooperator_api_log_action",
    ),
    (
        "cooperator_api_logs.emc_api_log_menu",
        "cooperator_api_logs.cooperator_api_log_menu",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming models")
    openupgrade.rename_models(env.cr, renamed_models)
    _logger.info("renaming tables")
    openupgrade.rename_tables(env.cr, renamed_tables)
    _logger.info("renaming xmlids")
    openupgrade.renamed_xmlids(env.cr, renamed_xmlids)
