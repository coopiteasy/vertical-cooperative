# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited


from odoo import _

from odoo.addons.component.core import Component


class PingService(Component):
    _inherit = "base.rest.service"
    _name = "emc.services"
    _usage = "ping"  # service_name
    _collection = "emc.services"
    _description = """
        Ping services (test the api)
    """

    def search(self):
        return {"message": _("Called search on ping API")}

    def test(self):
        return {"message": _("Called ping on ping API")}

    def _validator_test(self):
        return {}

    def _validator_return_test(self):
        return {"message": {"type": "string"}}

    def _validator_search(self):
        return {}

    def _validator_return_search(self):
        return {"message": {"type": "string"}}
