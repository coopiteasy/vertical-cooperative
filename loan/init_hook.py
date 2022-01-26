import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

renamed_modules = {
    "easy_my_coop_loan": "loan",
}


def pre_init_hook(cr):
    """
    Check if an old installation of easy_my_coop_loan exists. If so, it
    will be replaced by this module.
    """
    # TODO: check that easy_my_coop_loan is installed before running
    # this script !

    # This script is run after that odoo update the application module
    # list. So the new 'loan' module already has been added to the
    # ir_module_module table. So we should consider that renaming
    # easy_my_coop_loan is like merging it in the not yet installed new
    # module loan.
    _logger.info("before pre-migration script")
    openupgrade.update_module_names(cr, renamed_modules.items(),
                                    merge_modules=True)
    _logger.info("after pre-migration script")
