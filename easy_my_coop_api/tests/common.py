# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import requests
import odoo

from odoo.addons.base_rest.tests.common import BaseRestCase

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCase(BaseRestCase):
    def setUp(self):
        super().setUp()
        self.session = requests.Session()

    def http_get(self, url):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return self.session.get(url)

    def http_post(self, url, data):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return self.session.post(url, data=data)
