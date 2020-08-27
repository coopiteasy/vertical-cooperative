# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import re

from odoo import http
from odoo.http import route

from odoo.addons.base_rest.controllers import main


def patch_for_json(path_re):
    # this is to avoid Odoo, which assumes json always means json+rpc,
    # complaining about "function declared as capable of handling request
    # of type 'http' but called with a request of type 'json'"
    # cf rest-framework/graphql_base/controllers/main.py
    path_re = re.compile(path_re)
    orig_get_request = http.Root.get_request

    def get_request(self, httprequest):
        if path_re.match(httprequest.path):
            return http.HttpRequest(httprequest)
        return orig_get_request(self, httprequest)

    http.Root.get_request = get_request


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

    patch_for_json("^/api/subscription-request/[0-9]*/validate$")
