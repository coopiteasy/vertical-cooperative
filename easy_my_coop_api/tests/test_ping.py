# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import json

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext

from .common import BaseEMCRestCase


class TestPing(BaseEMCRestCase):
    def test_public_service(self):
        collection = _PseudoCollection("emc.services", self.env)
        emc_services_env = WorkContext(
            model_name="rest.service.registration", collection=collection
        )

        service = emc_services_env.component(usage="ping")
        result = service.test()

        self.assertTrue("message" in result)

    def test_ping_route(self):
        response = self.http_get("/api/ping/test")
        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content)
        self.assertTrue("message" in content)

    def test_search_route(self):
        self.login("manager-emc", "demo")
        response = self.http_get("/api/ping")
        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content)
        self.assertTrue("message" in content)
