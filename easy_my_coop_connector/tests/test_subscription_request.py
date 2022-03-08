# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import datetime
from unittest.mock import Mock, patch

import requests

from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase

from .test_data import SR_GET_RESULT, SR_SEARCH_RESULT, SR_VALIDATE_RESULT, dict_to_dump


class EMCSRConnectorCase(EMCBaseCase):
    def setUp(self):
        super().setUp()
        self.backend = self.browse_ref("easy_my_coop_connector.emc_backend_demo")
        self.share_type_B_pt = self.browse_ref(
            "easy_my_coop.product_template_share_type_2_demo"
        )
        self.share_type_B_pp = self.share_type_B_pt.product_variant_id

    def test_search_and_get_requests(self):
        SubscriptionRequest = self.env["subscription.request"]
        SRBinding = self.env["emc.binding.subscription.request"]

        date_to = datetime.date.today()
        date_from = date_to - datetime.timedelta(days=1)

        with patch.object(requests, "get") as mock_get:
            # todo use request_mock library
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(SR_SEARCH_RESULT)

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
        self.assertEquals(srequest.lastname, "Dublues")
        self.assertEquals(srequest.share_product_id.id, self.share_type_B_pp.id)
        self.assertEquals(
            srequest.subscription_amount, self.share_type_B_pt.list_price * 3
        )

        with patch.object(requests, "get") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(SR_GET_RESULT)

            SubscriptionRequest.backend_read(external_id)

        self.assertEquals(srequest.firstname, "Robin")
        self.assertEquals(srequest.phone, False)
        self.assertEquals(srequest.firstname, "Robin")
        self.assertEquals(srequest.iban, "98765434567")

    def test_validate_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "put") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(SR_VALIDATE_RESULT)

            srequest.validate_subscription_request()

        self.assertEquals(srequest.state, "done")

        # local invoice created
        self.assertTrue(len(srequest.capital_release_request) > 0)
        # local invoice linked to external invoice
        self.assertEquals(
            srequest.capital_release_request.binding_id.external_id,
            SR_VALIDATE_RESULT["capital_release_request"][0],
        )

    def test_block_subscription_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "put") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response_content = SR_GET_RESULT.copy()
            response_content["state"] = "block"
            mock_response.content = dict_to_dump(response_content)

            srequest.block_subscription_request()

        self.assertEquals(srequest.state, "block")

    def test_unblock_subscription_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        srequest.state = "block"
        with patch.object(requests, "put") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response_content = SR_GET_RESULT.copy()
            response_content["state"] = "draft"
            mock_response.content = dict_to_dump(response_content)
            srequest.unblock_subscription_request()

        self.assertEquals(srequest.state, "draft")

    def test_cancel_subscription_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "put") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response_content = SR_GET_RESULT.copy()
            response_content["state"] = "cancelled"
            mock_response.content = dict_to_dump(response_content)
            srequest.cancel_subscription_request()

        self.assertEquals(srequest.state, "cancelled")

    def test_put_on_waiting_list(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "put") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response_content = SR_GET_RESULT.copy()
            response_content["state"] = "waiting"
            mock_response.content = dict_to_dump(response_content)
            srequest.put_on_waiting_list()

        self.assertEquals(srequest.state, "waiting")

    # todo test 400
