# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import json

import requests
from lxml import html

import odoo
from odoo.fields import Date

from odoo.addons.base_rest.tests.common import BaseRestCase

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCase(BaseRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.AuthApiKey = cls.env["auth.api.key"]
        cls.api_key_test = cls.env.ref(
            "easy_my_coop_api.auth_api_key_manager_emc_demo"
        )

    def _add_api_key(self, headers):
        key_dict = {"API-KEY": self.api_key_test.key}
        if headers:
            headers.update(key_dict)
        else:
            headers = key_dict
        return headers

    def setUp(self):
        super().setUp()
        self.session = requests.Session()
        self.demo_request_1 = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        self.demo_request_2 = self.browse_ref(
            "easy_my_coop.subscription_request_2_demo"
        )
        self.demo_share_product = (
            self.demo_request_1.share_product_id.product_tmpl_id
        )

        date = Date.to_string(self.demo_request_1.date)
        self.demo_request_1_dict = {
            "id": self.demo_request_1.id,
            "name": "Manuel Dublues",
            "email": "manuel@demo.net",
            "date": date,
            "state": "draft",
            "ordered_parts": 3,
            "share_product": {
                "id": self.demo_share_product.id,
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
        }

    def http_get(self, url, headers=None):
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)

        return self.session.get(url, headers=headers)

    def http_get_content(self, route, headers=None):
        response = self.http_get(route, headers=headers)
        self.assertEquals(response.status_code, 200)
        content = response.content.decode("utf-8")
        return json.loads(content)

    def http_post(self, url, data, headers=None):
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)

        return self.session.post(url, json=data, headers=headers)

    @staticmethod
    def html_doc(response):
        """Get an HTML LXML document."""
        return html.fromstring(response.content)

    def login(self, login, password):
        url = "/web/login"
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)

        doc = self.html_doc(response)
        token = doc.xpath("//input[@name='csrf_token']")[0].get("value")

        response = self.http_post(
            url=url,
            data={"login": login, "password": password, "csrf_token": token},
        )
        self.assertEquals(response.status_code, 200)
        return response
