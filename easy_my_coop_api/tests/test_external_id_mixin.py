# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError

import odoo
from odoo.fields import Date
from odoo.tests import TransactionCase


class TestExternalIdMixin(TransactionCase):
    def test_res_partner_api_external_id(self):
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.assertFalse(partner._api_external_id)
        self.assertFalse(partner.external_id_sequence_id)

        external_id = partner.get_api_external_id()
        self.assertTrue(bool(partner._api_external_id))
        self.assertTrue(bool(partner.external_id_sequence_id))

        self.assertEquals(external_id, partner.get_api_external_id())

    def test_subscription_request_api_external_id(self):
        share_type = self.browse_ref(
            "easy_my_coop.product_template_share_type_2_demo"
        ).product_variant_id
        sr = self.env["subscription.request"].create(
            {
                "name": "test create request",
                "email": "test@demo.net",
                "address": "schaerbeekstraat",
                "zip_code": "1111",
                "city": "Brussels",
                "country_id": self.ref("base.be"),
                "date": Date.today(),
                "source": "manual",
                "ordered_parts": 3,
                "share_product_id": share_type.id,
                "lang": "en_US",
            }
        )
        self.assertFalse(sr._api_external_id)
        self.assertFalse(sr.external_id_sequence_id)

        external_id = sr.get_api_external_id()
        self.assertTrue(bool(sr._api_external_id))
        self.assertTrue(bool(sr.external_id_sequence_id))

        self.assertEquals(external_id, sr.get_api_external_id())

    def test_account_journal_api_external_id(self):
        bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "test",
                "partner_id": self.env.user.company_id.partner_id.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "test journal",
                "code": "123",
                "type": "bank",
                "company_id": self.env.ref("base.main_company").id,
                "bank_account_id": bank.id,
            }
        )
        self.assertFalse(journal._api_external_id)
        self.assertFalse(journal.external_id_sequence_id)

        external_id = journal.get_api_external_id()
        self.assertTrue(bool(journal._api_external_id))
        self.assertTrue(bool(journal.external_id_sequence_id))

        self.assertEquals(external_id, journal.get_api_external_id())

    def test_account_invoice_api_external_id(self):
        invoice = self.env["account.invoice"].create({"name": "create passes"})
        self.assertFalse(invoice._api_external_id)
        self.assertFalse(invoice.external_id_sequence_id)

        external_id = invoice.get_api_external_id()
        self.assertTrue(bool(invoice._api_external_id))
        self.assertTrue(bool(invoice.external_id_sequence_id))

        self.assertEquals(external_id, invoice.get_api_external_id())

    @odoo.tools.mute_logger("odoo.sql_db")
    def test_duplicate_api_external_id_raises(self):
        invoice_1 = self.env["account.invoice"].create(
            {"name": "create passes"}
        )
        external_id = invoice_1.get_api_external_id()
        self.assertTrue(bool(invoice_1._api_external_id))

        invoice_2 = self.env["account.invoice"].create(
            {"name": "create passes"}
        )
        with self.assertRaises(IntegrityError):
            invoice_2._api_external_id = external_id
