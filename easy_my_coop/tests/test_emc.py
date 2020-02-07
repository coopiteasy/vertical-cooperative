# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Date
from odoo.exceptions import AccessError
from .test_base import EMCBaseCase


class EMCCase(EMCBaseCase):
    def setUp(self):
        super(EMCCase, self).setUp()

        self.request = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        self.bank_journal_euro = self.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )

    def test_put_on_waiting_list(self):
        self.as_emc_user()
        self.request.put_on_waiting_list()
        self.assertEquals(self.request.state, "waiting")

    def test_validate_subscription_request(self):
        self.as_emc_user()
        # todo missing structure fails the rules?
        self.request.validate_subscription_request()

        self.assertEquals(self.request.state, "done")
        self.assertTrue(self.request.partner_id)
        self.assertTrue(self.request.partner_id.coop_candidate)
        self.assertFalse(self.request.partner_id.member)
        self.assertEquals(self.request.type, "new")
        self.assertTrue(len(self.request.capital_release_request) >= 1)
        self.assertEquals(self.request.capital_release_request.state, "open")
        self.assertTrue(self.request.capital_release_request.sent)

    def test_register_payment_for_capital_release(self):
        self.as_emc_user()
        self.request.validate_subscription_request()
        invoice = self.request.capital_release_request

        ctx = {"active_model": "account.invoice", "active_ids": [invoice.id]}
        register_payments = (
            self.env["account.register.payments"]
            .with_context(ctx)
            .create(
                {
                    "payment_date": Date.today(),
                    "journal_id": self.bank_journal_euro.id,
                    "payment_method_id": self.payment_method_manual_in.id,
                }
            )
        )
        register_payments.create_payments()
        self.assertEquals(self.request.capital_release_request.state, "paid")

        partner = self.request.partner_id
        self.assertFalse(partner.coop_candidate)
        self.assertTrue(partner.member)
        self.assertTrue(partner.share_ids)
        self.assertEquals(self.request.partner_id.effective_date, Date.today())

        share = partner.share_ids[0]
        self.assertEquals(share.share_number, self.request.ordered_parts)
        self.assertEquals(
            share.share_product_id, self.request.share_product_id
        )
        self.assertEquals(share.effective_date, Date.today())

    def test_user_rights(self):

        request_values = {
            "name": "test create request",
            "email": "test@demo.net",
            "address": "schaerbeekstraat",
            "zip_code": "1111",
            "city": "Brussels",
            "country_id": self.ref("base.be"),
            "date": Date.today(),
            "source": "manual",
            "ordered_parts": 3,
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
            "lang": "en_US",
        }

        # test ir model access for base user
        self.as_user()
        read_request = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        with self.assertRaises(AccessError):
            read_request.name = "test write request"
        with self.assertRaises(AccessError):
            self.env["subscription.request"].create(request_values)
        with self.assertRaises(AccessError):
            read_request.unlink()

        share_line = self.browse_ref("easy_my_coop.share_line_1_demo")
        with self.assertRaises(AccessError):
            share_line.share_number = 3

        # test ir model access for easy my coop user
        self.as_emc_user()
        read_request = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        read_request.name = "test write request"
        create_request = self.env["subscription.request"].create(
            request_values
        )
        with self.assertRaises(AccessError):
            create_request.unlink()

        share_line = self.browse_ref("easy_my_coop.share_line_1_demo")
        share_line.share_number = 3
        with self.assertRaises(AccessError):
            share_line.unlink()

        share_type = self.browse_ref(
            "easy_my_coop.product_template_share_type_1_demo"
        )
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

        # test ir model access for easy my coop manager
        self.as_emc_manager()
        read_request = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        read_request.name = "test write request"
        create_request = self.env["subscription.request"].create(
            request_values
        )
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

    def test_validated_lines_on_subscription_request(self):
        request = self.request
        request.skip_control_ng = False

        self.assertFalse(request.skip_control_ng)
        self.assertFalse(request.iban)

        # empty iban - don't skip
        self.assertFalse(request.validated)

        # good iban - don't skip
        request.skip_control_ng = False
        self.request.iban = "BE71096123456769"
        self.assertTrue(request.validated)

        # wrong iban - don't skip
        self.request.iban = "xxxx"
        self.assertFalse(request.validated)

        # wrong iban - skip
        request.skip_control_ng = True
        self.assertTrue(request.validated)

        # empty iban - skip
        self.request.iban = False
        self.assertTrue(request.validated)
