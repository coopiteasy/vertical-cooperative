import logging

from openupgradelib import openupgrade

logger = logging.getLogger("OpenUpgrade")


@openupgrade.migrate()
def migrate(env, version):
    # Set all values 'easy_my_coop' to True for mail templates belonging to the
    # easy_my_coop% modules. (T2772)
    domain = [("model", "=", "mail.template"), ("module", "=like", "easy_my_coop%")]
    templates = env["ir.model.data"].search(domain)
    for entry in templates:
        if not entry.easy_my_coop:
            logger.info(
                "Changing field 'easy_my_coop' from False to True in '{}'".format(
                    "{}.{}".format(entry.module, entry.name)
                )
            )
            entry.easy_my_coop = True
