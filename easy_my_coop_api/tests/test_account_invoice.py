# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Date

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext

from .common import BaseEMCRestCase


class TestAccountInvoiceController(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)

    def setUp(self):
        res = super().setUp()
        collection = _PseudoCollection("emc.services", self.env)
        emc_services_env = WorkContext(
            model_name="rest.service.registration", collection=collection
        )
        self.ai_service = emc_services_env.component(usage="invoice")

        self.share_type_A = self.browse_ref(
            "easy_my_coop.product_template_share_type_1_demo"
        )
        self._capital_release_create()

        today = Date.to_string(Date.today())
        self.demo_invoice_dict = {
            "id": 1,
            "number": "xxx",  # can't guess it
            "partner": {"id": 1, "name": "Catherine des Champs"},
            "account": {"id": 1, "name": "Cooperators"},
            "journal": {"id": 1, "name": "Subscription Journal"},
            "subscription_request": {},
            "state": "open",
            "date": today,
            "date_invoice": today,
            "date_due": today,
            "type": "out_invoice",
            "invoice_lines": [
                {
                    "name": "Share Type A",
                    "product": {"id": 1, "name": "Part A - Founder"},
                    "price_unit": 100.0,
                    "quantity": 2.0,
                    "account": {"id": 2, "name": "Equity"},
                }
            ],
        }
        return res

    def _capital_release_create(self):
        self.coop_candidate = self.env["res.partner"].create(
            {
                "name": "Catherine des Champs",
                "company_id": self.company.id,
                "property_account_receivable_id": self.receivable.id,
                "property_account_payable_id": self.payable.id,
            }
        )

        capital_release_line = [
            (
                0,
                False,
                {
                    "name": "Share Type A",
                    "account_id": self.equity_account.id,
                    "quantity": 2.0,
                    "price_unit": 100.0,
                    "product_id": self.share_type_A.product_variant_id.id,
                },
            )
        ]

        self.capital_release = self.env["account.invoice"].create(
            {
                "number": "Capital Release Example",
                "partner_id": self.coop_candidate.id,
                "type": "out_invoice",
                "invoice_line_ids": capital_release_line,
                "account_id": self.cooperator_account.id,
                "journal_id": self.subscription_journal.id,
            }
        )
        self.capital_release.action_invoice_open()

    def test_service_get(self):
        external_id = self.capital_release.get_api_external_id()
        result = self.ai_service.get(external_id)
        expected = self.demo_invoice_dict.copy()
        expected["number"] = result["number"]
        self.assertEquals(expected, result)

    def test_route_get(self):
        external_id = self.capital_release.get_api_external_id()
        route = "/api/invoice/%s" % external_id
        content = self.http_get_content(route)
        expected = self.demo_invoice_dict.copy()
        expected["number"] = content["number"]
        self.assertEquals(expected, content)
