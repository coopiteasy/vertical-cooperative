# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# undefined name 'env'
env = env  # noqa: F821

renamed_modules = {
    "easy_my_coop": "cooperator",
}

_logger.info("rename easy_my_coop_x modules to cooperator_x")
openupgrade.update_module_names(env.cr, renamed_modules.items())
env.cr.commit()
