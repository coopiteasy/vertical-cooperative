# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

from odoo.addons.component.core import AbstractComponent


class BaseRestService(AbstractComponent):
    _name = "emc.rest.service"
    _inherit = "base.rest.service"
    _collection = "emc.services"
    _description = """
        Base Rest Services
    """

    def _one_to_many_to_dict(self, record):
        if record:
            return {"id": record.get_api_external_id(), "name": record.name}
        else:
            return {}

    def _or_none(self, value):
        if value:
            return value
        else:
            return None
