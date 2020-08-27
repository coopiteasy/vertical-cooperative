# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.http import route

from odoo.addons.base_rest.controllers import main


class UserController(main.RestController):
    _root_path = "/api/"
    _collection_name = "emc.services"
    _default_auth = "api_key"

    @route(
        _root_path + "<string:_service_name>/test",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    def test(self, _service_name):
        return self._process_method(
            _service_name, "test", _id=None, params=None
        )

    @route(
        _root_path + "<string:_service_name>/<int:_id>/validate",
        methods=["POST"],
        csrf=False,
    )
    def validate(self, _service_name, _id, **params):
        return self._process_method(
            _service_name, "validate", _id=_id, params=params
        )
