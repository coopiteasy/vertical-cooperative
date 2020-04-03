# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import requests
import json
import odoo
from lxml import html

from odoo.addons.base_rest.tests.common import BaseRestCase

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCase(BaseRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.AuthApiKey = cls.env["auth.api.key"]
        emc_manager = cls.env.ref("easy_my_coop.res_users_manager_emc_demo")
        cls.api_key_test = cls.AuthApiKey.create(
            {"name": "test-key", "key": "api-key", "user_id": emc_manager.id}
        )

    def setUp(self):
        super().setUp()
        self.session = requests.Session()
        self.demo_request_1 = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        self.demo_request_1_dict = {
            "id": self.demo_request_1.id,
            "name": "Manuel Dublues",
            "email": "manuel@demo.net",
            "date": "2020-02-23",
            "ordered_parts": 3,
            "share_product": {
                "id": self.demo_request_1.share_product_id.id,
                "name": "Part B - Worker",
            },
            "address": {
                "street": "schaerbeekstraat",
                "zip_code": "1111",
                "city": "Brussels",
                "country": "BE",
            },
            "lang": "en_US",
        }

    def http_get(self, url, headers=None):
        key_dict = {"API-KEY": "api-key"}
        if headers:
            headers.update(key_dict)
        else:
            headers = key_dict

        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return self.session.get(url, headers=headers)

    def http_get_content(self, route, headers=None):
        response = self.http_get(route, headers=headers)
        self.assertEquals(response.status_code, 200)

        return json.loads(response.content)

    def http_post(self, url, data):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return self.session.post(url, data=data)

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
