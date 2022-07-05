# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.exceptions import AccessError
from odoo.fields import Date

from .test_base import CooperatorBaseCase


class CooperatorCase(CooperatorBaseCase):
    def setUp(self):
        super().setUp()

        self.request = self.browse_ref("cooperator.subscription_request_1_demo")
        self.bank_journal_euro = self.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )

    def test_put_on_waiting_list(self):
        self.as_cooperator_user()
        self.request.put_on_waiting_list()
        self.assertEqual(self.request.state, "waiting")

    def test_validate_subscription_request(self):
        self.as_cooperator_user()
        # todo missing structure fails the rules?
        self.request.validate_subscription_request()

        self.assertEqual(self.request.state, "done")
        self.assertTrue(self.request.partner_id)
        self.assertTrue(self.request.partner_id.coop_candidate)
        self.assertFalse(self.request.partner_id.member)
        self.assertEqual(self.request.type, "new")
        self.assertTrue(len(self.request.capital_release_request) >= 1)
        self.assertEqual(self.request.capital_release_request.state, "posted")
        self.assertEqual(
            self.request.capital_release_request.invoice_payment_state, "not_paid"
        )

    def _pay_invoice(self, invoice, payment_date=None):
        ctx = {"active_model": "account.move", "active_ids": [invoice.id]}
        register_payment_vals = {
            "journal_id": self.bank_journal_euro.id,
            "payment_method_id": self.payment_method_manual_in.id,
        }
        if payment_date is not None:
            register_payment_vals["payment_date"] = payment_date
        register_payment = (
            self.env["account.payment.register"]
            .with_context(ctx)
            .create(register_payment_vals)
        )
        register_payment.create_payments()

    def test_register_payment_for_capital_release(self):
        self.as_cooperator_user()
        self.request.validate_subscription_request()
        invoice = self.request.capital_release_request

        self._pay_invoice(invoice)
        self.assertEqual(
            self.request.capital_release_request.invoice_payment_state, "paid"
        )

        partner = self.request.partner_id
        self.assertFalse(partner.coop_candidate)
        self.assertTrue(partner.member)
        self.assertTrue(partner.share_ids)
        self.assertEqual(partner.effective_date, Date.today())

        share = partner.share_ids[0]
        self.assertEqual(share.share_number, self.request.ordered_parts)
        self.assertEqual(share.share_product_id, self.request.share_product_id)
        self.assertEqual(share.effective_date, Date.today())

    def test_effective_date_from_payment_date(self):
        self.as_cooperator_user()
        self.request.validate_subscription_request()
        invoice = self.request.capital_release_request
        self._pay_invoice(invoice, datetime.date(2022, 6, 21))

        partner = self.request.partner_id
        self.assertEqual(partner.effective_date, datetime.date(2022, 6, 21))

    def test_user_rights(self):

        request_values = {
            "firstname": "test",
            "lastname": "create request",
            "email": "test@demo.net",
            "address": "schaerbeekstraat",
            "zip_code": "1111",
            "city": "Brussels",
            "country_id": self.ref("base.be"),
            "date": Date.today(),
            "source": "manual",
            "ordered_parts": 3,
            "share_product_id": self.browse_ref(
                "cooperator.product_template_share_type_2_demo"
            ).product_variant_id.id,
            "lang": "en_US",
        }

        # test ir model access for base user
        self.as_user()
        read_request = self.browse_ref("cooperator.subscription_request_1_demo")
        with self.assertRaises(AccessError):
            read_request.name = "test write request"
        with self.assertRaises(AccessError):
            self.env["subscription.request"].create(request_values)
        with self.assertRaises(AccessError):
            read_request.unlink()

        share_line = self.browse_ref("cooperator.share_line_1_demo")
        with self.assertRaises(AccessError):
            share_line.share_number = 3

        # test ir model access for cooperator coop user
        self.as_cooperator_user()
        read_request = self.browse_ref("cooperator.subscription_request_1_demo")
        read_request.name = "test write request"
        create_request = self.env["subscription.request"].create(request_values)
        with self.assertRaises(AccessError):
            create_request.unlink()

        share_line = self.browse_ref("cooperator.share_line_1_demo")
        share_line.share_number = 3
        with self.assertRaises(AccessError):
            share_line.unlink()

        share_type = self.browse_ref("cooperator.product_template_share_type_1_demo")
        share_type.list_price = 30
        with self.assertRaises(AccessError):
            self.env["product.template"].create(
                {
                    "name": "Part C - Client",
                    "short_name": "Part C",
                    "is_share": True,
                    "default_share_product": True,
                    "force_min_qty": True,
                    "minimum_quantity": 2,
                    "by_individual": True,
                    "by_company": True,
                    "list_price": 50,
                    "display_on_website": True,
                }
            )
        with self.assertRaises(AccessError):
            share_type.unlink()

        # test ir model access for cooperator manager
        self.as_cooperator_manager()
        read_request = self.browse_ref("cooperator.subscription_request_1_demo")
        read_request.name = "test write request"
        create_request = self.env["subscription.request"].create(request_values)
        with self.assertRaises(AccessError):
            create_request.unlink()

        share_type = self.env["product.template"].create(
            {
                "name": "Part C - Client",
                "short_name": "Part C",
                "is_share": True,
                "default_share_product": True,
                "force_min_qty": True,
                "minimum_quantity": 2,
                "by_individual": True,
                "by_company": True,
                "list_price": 50,
                "display_on_website": True,
            }
        )
        share_type.list_price = 30
        share_type.unlink()

    def test_compute_is_valid_iban_on_subscription_request(self):
        request = self.request
        request.iban = False
        request.skip_iban_control = False

        # empty iban - don't skip
        self.assertFalse(request.is_valid_iban)

        # good iban - don't skip
        self.request.iban = "BE71096123456769"
        self.assertTrue(request.is_valid_iban)

        # wrong iban - don't skip
        self.request.iban = "xxxx"
        self.assertFalse(request.is_valid_iban)

        # wrong iban - don't skip
        self.request.iban = "BE71096123456760"
        self.assertFalse(request.is_valid_iban)

        # wrong iban - skip
        request.skip_iban_control = True
        self.assertTrue(request.is_valid_iban)

        # empty iban - skip
        self.request.iban = False
        self.assertTrue(request.is_valid_iban)
