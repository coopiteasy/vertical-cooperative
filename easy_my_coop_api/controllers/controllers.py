# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import datetime

from odoo.http import request, route

from odoo.addons.base_rest.controllers import main


class UserController(main.RestController):
    _root_path = "/api/"
    _collection_name = "emc.services"
    _default_auth = "api_key"

    def _process_method(self, service_name, method_name, *args, params=None):
        response = super()._process_method(
            service_name, method_name, *args, params=params
        )
        # only admin can create emc.api.log
        # only log successful calls
        self.collection.env["emc.api.log"].sudo().create(
            {
                "datetime": datetime.now(),
                "method": request.httprequest.method,
                "path": request.httprequest.path,
                "headers": request.httprequest.headers,
                "payload": request.httprequest.data,
                "response": response.data,
                "status": response.status_code,
            }
        )
        return response

    @route(
        _root_path + "<string:_service_name>/test",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    def test(self, _service_name):
        return self._process_method(_service_name, "test", params=None)
