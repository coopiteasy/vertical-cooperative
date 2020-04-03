# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import date, timedelta
import odoo
from odoo.fields import Date
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext

from .common import BaseEMCRestCase


class TestSRController(BaseEMCRestCase):
    def setUp(self):
        super().setUp()
        collection = _PseudoCollection("emc.services", self.env)
        emc_services_env = WorkContext(
            model_name="rest.service.registration", collection=collection
        )

        self.service = emc_services_env.component(usage="subscription_request")

    def test_service(self):
        # kept as example
        # useful if you need to change data in database and check db type

        result = self.service.get(self.demo_request_1.id)
        self.assertEquals(self.demo_request_1_dict, result)

        all_sr = self.service.search()
        self.assertTrue(all_sr)

        sr_date = self.demo_request_1.date
        date_from = Date.to_string(sr_date - timedelta(days=1))
        date_to = Date.to_string(sr_date + timedelta(days=1))

        date_sr = self.service.search(date_from=date_from, date_to=date_to)
        self.assertTrue(date_sr)

    def test_route_get(self):
        id_ = self.demo_request_1.id
        route = "/api/subscription_request/%s" % id_
        content = self.http_get_content(route)
        self.assertEquals(self.demo_request_1_dict, content)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_returns_not_found(self):
        route = "/api/subscription_request/%s" % "99999"
        response = self.http_get(route)
        self.assertEquals(response.status_code, 404)

    def test_route_get_string_returns_method_not_allowed(self):
        route = "/api/subscription_request/%s" % "abc"
        response = self.http_get(route)
        self.assertEquals(response.status_code, 405)

    def test_route_search_all(self):
        route = "/api/subscription_request"
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

    def test_route_search_by_date(self):
        sr_date = self.demo_request_1.date
        date_from = Date.to_string(sr_date - timedelta(days=1))
        date_to = Date.to_string(sr_date + timedelta(days=1))

        route = "/api/subscription_request?date_from=%s" % date_from
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

        route = "/api/subscription_request?date_to=%s" % date_to
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

        route = "/api/subscription_request?date_from=%s&date_to=%s" % (
            date_from,
            date_to,
        )
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

        route = "/api/subscription_request?date_from=%s" % "2300-01-01"
        content = self.http_get_content(route)
        self.assertEquals(content["count"], 0)

        route = "/api/subscription_request?date_to=%s" % "1900-01-01"
        content = self.http_get_content(route)
        self.assertEquals(content["count"], 0)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_search_acd_date_returns_bad_request(self):
        route = "/api/subscription_request?date_from=%s" % "20200101"
        response = self.http_get(route)
        self.assertEquals(response.status_code, 400)

    # def test_route_create(self):
