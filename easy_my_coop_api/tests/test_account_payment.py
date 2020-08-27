# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Date

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext

from .common import BaseEMCRestCase


class TestAccountPaymentController(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)

    def setUp(self):
        res = super().setUp()
        collection = _PseudoCollection("emc.services", self.env)
        emc_services_env = WorkContext(
            model_name="rest.service.registration", collection=collection
        )
        self.ap_service = emc_services_env.component(usage="payment")
        self.ai_service = emc_services_env.component(usage="invoice")
        self.demo_request_1 = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        return res

    def test_service_create(self):
        self.demo_request_1.validate_subscription_request()
        invoice = self.demo_request_1.capital_release_request
        journal = self.bank_journal

        result = self.ap_service.create(
            payment_date=Date.to_string(Date.today()),
            amount=self.demo_request_1.subscription_amount,
            payment_type="inbound",
            payment_method="manual",
            communication=invoice.reference,
            invoice=invoice.get_api_external_id(),
            journal=journal.get_api_external_id(),
        )

        demo_payment_dict = {
            "id": result["id"],
            "communication": invoice.reference,
            "invoice": {
                "id": invoice.get_api_external_id(),
                "name": invoice.number,
            },
            "amount": self.demo_request_1.subscription_amount,
            "payment_date": Date.to_string(Date.today()),
            "journal": {
                "id": self.bank_journal.get_api_external_id(),
                "name": self.bank_journal.name,
            },
        }
        self.assertEquals(demo_payment_dict, result)

        invoice = self.ai_service.get(invoice.get_api_external_id())
        self.assertEquals("paid", invoice["state"])

    # def test_route_create(self):  # todo
    #     external_id = self.capital_release.get_api_external_id()
    #     route = "/api/payment/%s" % external_id
    #     content = self.http_get_content(route)
    #     self.assertEquals(self.demo_payment_dict, content)
