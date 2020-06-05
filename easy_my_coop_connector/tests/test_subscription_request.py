# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import datetime
import json
from unittest.mock import Mock, patch

import requests

from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase

NOT_FOUND_ERROR = {"name": "Not Found", "code": 404}
FORBIDDEN_ERROR = {"name": "Forbidden", "code": 403}
SERVER_ERROR = {"name": "Server Error", "code": 500}
NO_RESULT = {"count": 0, "rows": []}
SEARCH_RESULT = {
    "count": 1,
    "rows": [
        {
            "id": 1,
            "date": "2020-05-14",
            "email": "manuel@demo.net",
            "address": {
                "city": "Brussels",
                "street": "schaerbeekstraat",
                "zip_code": "1111",
                "country": "BE",
            },
            "lang": "en_US",
            "ordered_parts": 3,
            "name": "Manuel Dublues",
            "share_product": {"name": "Part B - Worker", "id": 31},
            "state": "draft",
        }
    ],
}
GET_RESULT = {
    "id": 1,
    "name": "Robin Des Bois",
    "date": "2020-05-14",
    "email": "manuel@demo.net",
    "address": {
        "city": "Brussels",
        "street": "schaerbeekstraat",
        "zip_code": "1111",
        "country": "BE",
    },
    "lang": "en_US",
    "ordered_parts": 3,
    "share_product": {"name": "Part B - Worker", "id": 31},
    "state": "draft",
}

VALIDATE_RESULT = {
    "id": 9999,
    "number": "SUBJ/2020/001",
    "date_due": "2020-08-12",
    "state": "open",
    "date_invoice": "2020-08-12",
    "date": "2020-08-12",
    "type": "out_invoice",
    "subscription_request": {"name": "Manuel Dublues", "id": 1},
    "partner": {"name": "Manuel Dublues", "id": 1},
    "invoice_lines": [
        {
            "price_unit": 25.0,
            "quantity": 3.0,
            "account": {"name": "Product Sales", "id": 2},
            "name": "Part B - Worker",
            "product": {"name": "Part B - Worker", "id": 2},
        }
    ],
    "journal": {"name": "Subscription Journal", "id": 1},
    "account": {"name": "Cooperators", "id": 1},
}


def dict_to_dump(content):
    return json.dumps(content).encode("utf-8")


class EMCConnectorCase(EMCBaseCase):
    def setUp(self):
        super().setUp()
        self.backend = self.browse_ref(
            "easy_my_coop_connector.emc_backend_demo"
        )
        self.share_type_B_pt = self.browse_ref(
            "easy_my_coop.product_template_share_type_2_demo"
        )
        self.share_type_B_pp = self.share_type_B_pt.product_variant_id

    def test_search_requests(self):
        SubscriptionRequest = self.env["subscription.request"]
        SRBinding = self.env["emc.binding.subscription.request"]

        date_to = datetime.date.today()
        date_from = date_to - datetime.timedelta(days=1)

        with patch.object(requests, "get") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(SEARCH_RESULT)

            SubscriptionRequest.fetch_subscription_requests(
                date_from=date_from, date_to=date_to
            )

        external_id = 1
        binding = SRBinding.search_binding(self.backend, external_id)
        self.assertTrue(
            bool(binding),
            "no binding created when searching subscription requests",
        )

        srequest = binding.internal_id
        self.assertEquals(srequest.name, "Manuel Dublues")
        self.assertEquals(
            srequest.share_product_id.id, self.share_type_B_pp.id
        )
        self.assertEquals(
            srequest.subscription_amount, self.share_type_B_pt.list_price * 3
        )

        with patch.object(requests, "get") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(GET_RESULT)

            SubscriptionRequest.backend_read(external_id)

        self.assertEquals(srequest.name, "Robin Des Bois")

    def test_validate_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "post") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(VALIDATE_RESULT)

            srequest.validate_subscription_request()

        self.assertEquals(srequest.state, "done")

        # local invoice created
        self.assertTrue(len(srequest.capital_release_request) > 0)
        # local invoice linked to external invoice
        self.assertEquals(
            srequest.capital_release_request.binding_id.external_id,
            VALIDATE_RESULT["id"],
        )

    # todo test 400
