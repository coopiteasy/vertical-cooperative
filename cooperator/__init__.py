from . import models
from . import report
from . import wizard


from openupgradelib import openupgrade


@openupgrade.migrate()
def uninstall_previous_version(env, version):

    # uninstall the previous version of the module
    module_ids = env["ir.module.module"].search(
        [("name", "=", "easy_my_coop"), ("state", "=", "installed")]
    )
    if module_ids:
        module_ids.button_uninstall()
