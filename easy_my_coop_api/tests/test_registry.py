# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import odoo
from odoo.http import controllers_per_module

from odoo.addons.base_rest.tests.common import BaseRestCase

from ..controllers.controllers import UserController

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class TestControllerRegistry(BaseRestCase):
    def test_controller_registry(self):
        controllers = controllers_per_module["easy_my_coop_api"]
        self.assertEqual(len(controllers), 1)
        self.assertIn(
            (
                "odoo.addons.easy_my_coop_api"
                ".controllers.controllers.UserController",
                UserController,
            ),
            controllers,
        )
