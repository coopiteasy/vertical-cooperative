# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from datetime import timedelta

from werkzeug.exceptions import BadRequest

import odoo
from odoo.exceptions import AccessError
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

        self.sr_service = emc_services_env.component(usage="subscription-request")

        self.demo_request_1 = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        self.demo_request_2 = self.browse_ref(
            "easy_my_coop.subscription_request_waiting_demo"
        )
        self.demo_share_product = self.demo_request_1.share_product_id.product_tmpl_id

        date = Date.to_string(self.demo_request_1.date)
        self.demo_request_1_dict = {
            "id": self.demo_request_1.get_api_external_id(),
            "name": "Manuel Dublues",
            "email": "manuel@demo.net",
            "date": date,
            "state": "draft",
            "ordered_parts": 3,
            "share_product": {
                "id": self.demo_share_product.get_api_external_id(),
                "name": self.demo_share_product.name,
            },
            "address": {
                "street": "schaerbeekstraat",
                "zip_code": "1111",
                "city": "Brussels",
                "country": "BE",
            },
            "lang": "en_US",
            "capital_release_request": [],
            "data_policy_approved": True,
            "internal_rules_approved": True,
            "financial_risk_approved": True,
        }

    def test_service(self):
        # kept as example
        # useful if you need to change data in database and check db type

        result = self.sr_service.get(self.demo_request_1.get_api_external_id())
        self.assertEquals(self.demo_request_1_dict, result)

        all_sr = self.sr_service.search()
        self.assertTrue(all_sr)

        sr_date = self.demo_request_1.date
        date_from = Date.to_string(sr_date - timedelta(days=1))
        date_to = Date.to_string(sr_date + timedelta(days=1))

        date_sr = self.sr_service.search(date_from=date_from, date_to=date_to)
        self.assertTrue(date_sr)
        self.assertTrue(self.demo_request_1.first_api_export_date)
        self.assertTrue(self.demo_request_1.last_api_export_date)

    def test_fetched_request_cannot_be_updated(self):
        external_id = self.demo_request_1.get_api_external_id()
        self.sr_service.get(external_id)
        with self.assertRaises(AccessError):
            self.demo_request_1.email = "other@email.be"

    def test_route_get(self):
        external_id = self.demo_request_1.get_api_external_id()
        route = "/api/subscription-request/%s" % external_id
        content = self.http_get_content(route)
        self.assertEquals(self.demo_request_1_dict, content)

    def test_route_search_all(self):
        route = "/api/subscription-request"
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

    def test_route_search_by_date(self):
        sr_date = self.demo_request_1.date
        date_from = Date.to_string(sr_date - timedelta(days=1))
        date_to = Date.to_string(sr_date + timedelta(days=1))

        route = "/api/subscription-request?date_from=%s" % date_from
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

        route = "/api/subscription-request?date_to=%s" % date_to
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

        route = "/api/subscription-request?date_from={}&date_to={}".format(
            date_from, date_to
        )
        content = self.http_get_content(route)
        self.assertIn(self.demo_request_1_dict, content["rows"])

        route = "/api/subscription-request?date_from=%s" % "2300-01-01"
        content = self.http_get_content(route)
        self.assertEquals(content["count"], 0)

        route = "/api/subscription-request?date_to=%s" % "1900-01-01"
        content = self.http_get_content(route)
        self.assertEquals(content["count"], 0)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_search_acd_date_returns_bad_request(self):
        route = "/api/subscription-request?date_from=%s" % "20200101"
        response = self.http_get(route)
        self.assertEquals(response.status_code, 400)

    def test_route_create(self):
        url = "/api/subscription-request"
        data = {
            "name": "Lisa des Danses",
            "email": "lisa@desdanses.be",
            "ordered_parts": 3,
            "share_product": self.demo_share_product.id,
            "address": {
                "street": "schaerbeekstraat",
                "zip_code": "1111",
                "city": "Brussels",
                "country": "BE",
            },
            "lang": "en_US",
            "data_policy_approved": True,
            "internal_rules_approved": True,
            "financial_risk_approved": True,
        }

        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content.decode("utf-8"))

        content.pop("id")  # can't know id in advance
        expected = {
            **data,
            **{
                "date": Date.to_string(Date.today()),
                "state": "draft",
                "share_product": {
                    "id": self.demo_share_product.get_api_external_id(),
                    "name": self.demo_share_product.name,
                },
                "capital_release_request": [],
            },
        }
        self.assertEquals(expected, content)

    def test_route_update(self):
        url = "/api/subscription-request/%s" % self.demo_request_1.get_api_external_id()
        data = {"email": "another@email.coop"}

        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content.decode("utf-8"))

        expected = self.demo_request_1_dict
        expected.update(data)
        self.assertEquals(expected, content)

    def test_route_validate(self):
        url = (
            "/api/subscription-request/%s/validate"
            % self.demo_request_1.get_api_external_id()
        )
        response = self.http_post(url, data={})
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content.decode("utf-8"))

        state = content.get("state")
        self.assertEquals(state, "open")

    def test_service_validate_draft_request(self):
        self.sr_service.validate(self.demo_request_1.get_api_external_id())
        self.assertEquals(self.demo_request_1.state, "done")
        self.assertTrue(len(self.demo_request_1.capital_release_request) > 0)

    def test_service_validate_done_request(self):
        self.demo_request_2.validate_subscription_request()
        with self.assertRaises(BadRequest):
            self.sr_service.validate(self.demo_request_2.get_api_external_id())

    def test_service_set_to_waiting_ok(self):
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "waiting"}
        self.sr_service.update(_id=_id, **payload)
        self.assertEquals(self.demo_request_1.state, "waiting")

    def test_service_set_to_waiting_nok(self):
        self.demo_request_1.put_on_waiting_list()
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "waiting"}
        with self.assertRaises(BadRequest):
            self.sr_service.update(_id=_id, **payload)

    def test_service_set_to_block_ok(self):
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "block"}
        self.sr_service.update(_id=_id, **payload)
        self.assertEquals(self.demo_request_1.state, "block")

    def test_service_set_to_block_nok(self):
        self.demo_request_1.put_on_waiting_list()
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "block"}
        with self.assertRaises(BadRequest):
            self.sr_service.update(_id=_id, **payload)

    def test_service_set_to_draft_ok(self):
        _id = self.demo_request_1.get_api_external_id()
        self.demo_request_1.block_subscription_request()
        payload = {"state": "draft"}
        self.sr_service.update(_id=_id, **payload)
        self.assertEquals(self.demo_request_1.state, "draft")

    def test_service_set_to_draft_nok(self):
        self.demo_request_1.validate_subscription_request()
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "draft"}
        with self.assertRaises(BadRequest):
            self.sr_service.update(_id=_id, **payload)

    def test_service_set_to_paid_nok(self):
        self.demo_request_1.validate_subscription_request()
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "paid"}
        with self.assertRaises(BadRequest):
            self.sr_service.update(_id=_id, **payload)

    def test_service_set_to_transfer_nok(self):
        self.demo_request_1.validate_subscription_request()
        _id = self.demo_request_1.get_api_external_id()
        payload = {"state": "transfer"}
        with self.assertRaises(BadRequest):
            self.sr_service.update(_id=_id, **payload)
