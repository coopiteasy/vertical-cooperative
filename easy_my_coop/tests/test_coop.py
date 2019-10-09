# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.fields import Date


class TestCoop(common.TransactionCase):
    def setUp(self):
        super(TestCoop, self).setUp()

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
        self.request.put_on_waiting_list()
        self.assertEquals(self.request.state, "waiting")

    def test_validate_subscription_request(self):
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
