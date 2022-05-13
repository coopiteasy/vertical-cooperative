# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

logger = logging.getLogger("OpenUpgrade")


@openupgrade.migrate()
def migrate(env, version):
    # Set all values 'easy_my_coop' to True for mail templates belonging to the
    # easy_my_coop% modules. (T2772)
    domain = [("model", "=", "mail.template"), ("module", "=like", "easy_my_coop%")]
    model_data = env["ir.model.data"].search(domain)
    templates = env["mail.template"].browse([md.res_id for md in model_data])
    model_data_by_res_id = {md.res_id: md for md in model_data}
    for entry in templates:
        if not entry.easy_my_coop:
            md = model_data_by_res_id[entry.id]
            logger.info(
                "Changing field 'easy_my_coop' from False to True in '{}'".format(
                    "{}.{}".format(md.module, md.name)
                )
            )
            entry.easy_my_coop = True
