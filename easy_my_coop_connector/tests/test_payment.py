# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from unittest.mock import Mock, patch

import requests

from odoo.fields import Date

from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase

from .test_data import AP_CREATE_RESULT, SR_VALIDATE_RESULT, dict_to_dump


class EMCPaymentConnectorCase(EMCBaseCase):
    def setUp(self):
        super().setUp()
        self.backend = self.browse_ref(
            "easy_my_coop_connector.emc_backend_demo"
        )
        self.env["emc.binding.account.journal"].create(
            {
                "backend_id": self.backend.id,
                "internal_id": self.bank_journal.id,
                "external_id": 1,
            }
        )

    def test_post_payment_sends_and_binds_request(self):
        srequest = self.browse_ref("easy_my_coop.subscription_request_1_demo")
        with patch.object(requests, "post") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(SR_VALIDATE_RESULT)

            srequest.validate_subscription_request()

        capital_release_request = srequest.capital_release_request

        payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        ctx = {
            "active_model": "account.invoice",
            "active_ids": [capital_release_request.id],
        }
        register_payments = (
            self.env["account.register.payments"]
            .with_context(ctx)
            .create(
                {
                    "payment_date": Date.today(),
                    "journal_id": self.bank_journal.id,
                    "payment_method_id": payment_method_manual_in.id,
                }
            )
        )

        with patch.object(requests, "post") as mock_get:
            mock_get.return_value = mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = dict_to_dump(AP_CREATE_RESULT)

            register_payments.create_payments()

        self.assertEquals(capital_release_request.state, "paid")

        payment = capital_release_request.payment_ids
        self.assertEquals(payment.state, "posted")
        self.assertEquals(payment.binding_id.external_id, 9876)
