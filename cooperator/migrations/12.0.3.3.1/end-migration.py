# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

logger = logging.getLogger("OpenUpgrade")


@openupgrade.migrate()
def migrate(env, version):
    # Set all values 'is_cooperator_template' to True for mail templates
    # belonging to the cooperator% modules. (T2772)
    domain = [("model", "=", "mail.template"), ("module", "=like", "cooperator%")]
    model_data = env["ir.model.data"].search(domain)
    templates = env["mail.template"].browse([md.res_id for md in model_data])
    model_data_by_res_id = {md.res_id: md for md in model_data}
    for entry in templates:
        if not entry.is_cooperator_template:
            md = model_data_by_res_id[entry.id]
            logger.info(
                "Changing field 'is_cooperator_template' from False to True "
                "in '{}'".format("{}.{}".format(md.module, md.name))
            )
            entry.is_cooperator_template = True
