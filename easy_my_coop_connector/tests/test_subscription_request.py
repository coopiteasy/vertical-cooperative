# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import datetime
from unittest.mock import Mock, patch

import requests

from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase

from .test_data import (
    SR_GET_RESULT,
    SR_SEARCH_RESULT,
    SR_VALIDATE_RESULT,
    dict_to_dump,
)


class EMCSRConnectorCase(EMCBaseCase):
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
            mock_response.content = dict_to_dump(SR_GET_RESULT)

            SubscriptionRequest.backend_read(external_id)

        self.assertEquals(srequest.name, "Robin Des Bois")

    def test_validate_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "post") as mock_get:
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
            SR_VALIDATE_RESULT["id"],
        )

    # todo test 400
