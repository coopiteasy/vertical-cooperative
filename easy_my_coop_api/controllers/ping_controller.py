# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.base_rest.controllers import main
from odoo.http import route


class PingController(main.RestController):
    _root_path = "/api/"
    _collection_name = "emc.services"
    _default_auth = "public"

    @route(
        _root_path + "<string:_service_name>/ping",
        methods=["GET"],
        csrf=False,
    )
    def test(self, _service_name, _id=None, **params):
        return self._process_method(
            _service_name, "ping", _id=_id, params=params
        )
