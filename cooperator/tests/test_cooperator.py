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
        self.assertEqual(self.request.capital_release_request.payment_state, "not_paid")

    def test_capital_release_request_name(self):
        self.as_cooperator_user()
        self.request.validate_subscription_request()
        self.assertEqual(
            self.request.capital_release_request.name,
            "SUBJ/{year}/001".format(year=datetime.date.today().year),
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
        register_payment.action_create_payments()

    def test_register_payment_for_capital_release(self):
        self.as_cooperator_user()
        self.request.validate_subscription_request()
        invoice = self.request.capital_release_request

        self._pay_invoice(invoice)
        self.assertEqual(self.request.capital_release_request.payment_state, "paid")

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

    def _get_dummy_subscription_requests_vals(self):
        return {
            "share_product_id": self.browse_ref(
                "cooperator.product_template_share_type_1_demo"
            ).product_variant_id.id,
            "ordered_parts": 2,
            "user_id": self.uid,
            "firstname": "first name",
            "lastname": "last name",
            "email": "email@example.net",
            "phone": "dummy phone",
            "address": "dummy street",
            "zip_code": "dummy zip",
            "city": "dummy city",
            "country_id": self.ref("base.be"),
            "lang": "en_US",
            "gender": "other",
            "birthdate": "1980-01-01",
            "iban": "BE71096123456769",
        }

    def _get_dummy_company_subscription_requests_vals(self):
        vals = self._get_dummy_subscription_requests_vals()
        vals["is_company"] = True
        vals["company_name"] = "dummy company"
        vals["company_email"] = "companyemail@example.net"
        vals["company_register_number"] = "dummy company register number"
        vals["contact_person_function"] = "dummy contact person function"
        return vals

    def _create_dummy_subscription_from_partner(self, partner):
        vals = self._get_dummy_subscription_requests_vals()
        vals["partner_id"] = partner.id
        return self.env["subscription.request"].create(vals)

    def _create_dummy_subscription_from_company_partner(self, partner):
        vals = self._get_dummy_company_subscription_requests_vals()
        vals["partner_id"] = partner.id
        return self.env["subscription.request"].create(vals)

    def _validate_subscription_request_and_pay(self, subscription_request):
        subscription_request.validate_subscription_request()
        self._pay_invoice(subscription_request.capital_release_request)

    def _create_dummy_cooperator(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
            }
        )
        subscription_request = self._create_dummy_subscription_from_partner(partner)
        self._validate_subscription_request_and_pay(subscription_request)
        return partner

    def _create_dummy_company_cooperator(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy company partner 1",
                "is_company": True,
            }
        )
        subscription_request = self._create_dummy_subscription_from_company_partner(
            partner
        )
        self._validate_subscription_request_and_pay(subscription_request)
        return partner

    def test_create_subscription_from_non_cooperator_partner(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
            }
        )
        subscription_request = self._create_dummy_subscription_from_partner(partner)
        self.assertTrue(partner.cooperator)
        self.assertFalse(partner.coop_candidate)
        self.assertFalse(partner.member)
        subscription_request.validate_subscription_request()
        self.assertTrue(partner.cooperator)
        self.assertTrue(partner.coop_candidate)
        self.assertFalse(partner.member)
        self._pay_invoice(subscription_request.capital_release_request)
        self.assertTrue(partner.cooperator)
        self.assertFalse(partner.coop_candidate)
        self.assertTrue(partner.member)

    def test_create_subscription_from_non_cooperator_company_partner(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "is_company": True,
            }
        )
        subscription_request = self._create_dummy_subscription_from_company_partner(
            partner
        )
        self.assertTrue(partner.cooperator)
        self.assertFalse(partner.coop_candidate)
        self.assertFalse(partner.member)
        subscription_request.validate_subscription_request()
        self.assertTrue(partner.cooperator)
        self.assertTrue(partner.coop_candidate)
        self.assertFalse(partner.member)
        self._pay_invoice(subscription_request.capital_release_request)
        self.assertTrue(partner.cooperator)
        self.assertFalse(partner.coop_candidate)
        self.assertTrue(partner.member)

    def test_create_multiple_subscriptions_from_non_cooperator_partner(self):
        """
        Test that creating a subscription from a partner that has no parts yet
        creates a subscription request with the correct type.
        """
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
            }
        )
        subscription_request = self._create_dummy_subscription_from_partner(partner)
        self.assertEqual(subscription_request.type, "new")
        subscription_request2 = self._create_dummy_subscription_from_partner(partner)
        self.assertEqual(subscription_request2.type, "increase")

    def test_create_multiple_subscriptions_from_non_cooperator_company_partner(self):
        """
        Test that creating a subscription from a company partner that has no
        parts yet creates a subscription request with the correct type.
        """
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "is_company": True,
            }
        )
        subscription_request = self._create_dummy_subscription_from_company_partner(
            partner
        )
        self.assertEqual(subscription_request.type, "new")
        subscription_request2 = self._create_dummy_subscription_from_company_partner(
            partner
        )
        self.assertEqual(subscription_request2.type, "increase")

    def test_create_subscription_from_cooperator_partner(self):
        """
        Test that creating a subscription from a cooperator partner creates a
        subscription request with the correct type.
        """
        partner = self._create_dummy_cooperator()
        subscription_request = self._create_dummy_subscription_from_partner(partner)
        self.assertEqual(subscription_request.type, "increase")

    def test_create_subscription_from_cooperator_company_partner(self):
        """
        Test that creating a subscription from a cooperator company partner
        creates a subscription request with the correct type.
        """
        partner = self._create_dummy_company_cooperator()
        subscription_request = self._create_dummy_subscription_from_company_partner(
            partner
        )
        self.assertEqual(subscription_request.type, "increase")

    def test_create_subscription_without_partner(self):
        subscription_request = self.env["subscription.request"].create(
            self._get_dummy_subscription_requests_vals()
        )
        self.assertEqual(subscription_request.type, "new")
        self.assertEqual(subscription_request.name, "first name last name")
        self.assertFalse(subscription_request.partner_id)
        subscription_request.validate_subscription_request()
        partner = subscription_request.partner_id
        self.assertTrue(partner)
        self.assertFalse(partner.is_company)
        self.assertEqual(partner.firstname, "first name")
        self.assertEqual(partner.lastname, "last name")
        self.assertEqual(partner.name, "first name last name")
        self.assertEqual(partner.email, "email@example.net")
        self.assertEqual(partner.phone, "dummy phone")
        self.assertEqual(partner.street, "dummy street")
        self.assertEqual(partner.zip, "dummy zip")
        self.assertEqual(partner.city, "dummy city")
        self.assertEqual(partner.country_id, self.browse_ref("base.be"))
        self.assertEqual(partner.lang, "en_US")
        self.assertEqual(partner.gender, "other")
        self.assertEqual(partner.birthdate_date, datetime.date(1980, 1, 1))
        self.assertTrue(partner.cooperator)

    def test_create_subscription_for_company_without_partner(self):
        vals = self._get_dummy_company_subscription_requests_vals()
        subscription_request = self.env["subscription.request"].create(vals)
        self.assertEqual(subscription_request.type, "new")
        self.assertEqual(subscription_request.name, "dummy company")
        self.assertFalse(subscription_request.partner_id)
        subscription_request.validate_subscription_request()
        partner = subscription_request.partner_id
        self.assertTrue(partner)
        self.assertTrue(partner.is_company)
        self.assertFalse(partner.firstname)
        self.assertEqual(partner.lastname, "dummy company")
        self.assertEqual(partner.name, "dummy company")
        self.assertEqual(partner.email, "companyemail@example.net")
        self.assertFalse(partner.phone)
        self.assertEqual(partner.street, "dummy street")
        self.assertEqual(partner.zip, "dummy zip")
        self.assertEqual(partner.city, "dummy city")
        self.assertEqual(partner.country_id, self.browse_ref("base.be"))
        self.assertEqual(partner.lang, "en_US")
        self.assertFalse(partner.gender)
        self.assertFalse(partner.birthdate_date)
        self.assertTrue(partner.cooperator)
        representative = partner.child_ids
        self.assertTrue(representative)
        self.assertFalse(representative.is_company)
        self.assertEqual(representative.type, "representative")
        self.assertEqual(representative.function, "dummy contact person function")
        self.assertEqual(representative.firstname, "first name")
        self.assertEqual(representative.lastname, "last name")
        self.assertEqual(representative.name, "first name last name")
        self.assertEqual(representative.email, "email@example.net")
        self.assertEqual(representative.phone, "dummy phone")
        self.assertEqual(representative.street, "dummy street")
        self.assertEqual(representative.zip, "dummy zip")
        self.assertEqual(representative.city, "dummy city")
        self.assertEqual(representative.country_id, self.browse_ref("base.be"))
        self.assertEqual(representative.lang, "en_US")
        self.assertEqual(representative.gender, "other")
        self.assertEqual(representative.birthdate_date, datetime.date(1980, 1, 1))
        # should this be true?
        self.assertTrue(representative.cooperator)

    def test_create_subscription_with_matching_email(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "email": "dummy@example.net",
            }
        )
        vals = self._get_dummy_subscription_requests_vals()
        vals["email"] = "dummy@example.net"
        subscription_request = self.env["subscription.request"].create(vals)
        self.assertEqual(subscription_request.partner_id, partner)

    def test_create_subscription_with_multiple_matching_email(self):
        self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "email": "dummy@example.net",
            }
        )
        partner2 = self.env["res.partner"].create(
            {
                "name": "dummy partner 2",
                "email": "dummy@example.net",
                "cooperator": True,
            }
        )
        vals = self._get_dummy_subscription_requests_vals()
        vals["email"] = "dummy@example.net"
        subscription_request = self.env["subscription.request"].create(vals)
        # if there are multiple email matches, take the one that is a
        # cooperator.
        self.assertEqual(subscription_request.partner_id, partner2)

    def test_create_subscription_with_matching_empty_email(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "email": "",
            }
        )
        vals = self._get_dummy_subscription_requests_vals()
        vals["email"] = ""
        subscription_request = self.env["subscription.request"].create(vals)
        self.assertNotEqual(subscription_request.partner_id, partner)

    def test_create_subscription_with_matching_space_email(self):
        partner = self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "email": "",
            }
        )
        vals = self._get_dummy_subscription_requests_vals()
        vals["email"] = " "
        subscription_request = self.env["subscription.request"].create(vals)
        self.assertNotEqual(subscription_request.partner_id, partner)

    def test_create_subscription_with_matching_company_register_number(self):
        # create a dummy person partner to check that the match is not done by
        # email for companies.
        self.env["res.partner"].create(
            {
                "name": "dummy partner 1",
                "email": "dummy@example.net",
            }
        )
        company_partner = self.env["res.partner"].create(
            {
                "name": "dummy company",
                "email": "dummycompany@example.net",
                "company_register_number": "dummy company register number",
                "is_company": True,
            }
        )
        vals = self._get_dummy_company_subscription_requests_vals()
        vals["email"] = "dummy@example.net"
        subscription_request = self.env["subscription.request"].create(vals)
        partner = subscription_request.partner_id
        self.assertEqual(partner, company_partner)
        # no representative is created
        self.assertFalse(partner.child_ids)

    def test_create_subscription_with_multiple_matching_company_register_number(self):
        self.env["res.partner"].create(
            {
                "name": "dummy company 1",
                "email": "dummycompany@example.net",
                "company_register_number": "dummy company register number",
                "is_company": True,
            }
        )
        company_partner2 = self.env["res.partner"].create(
            {
                "name": "dummy company 2",
                "email": "dummycompany@example.net",
                "company_register_number": "dummy company register number",
                "is_company": True,
                "cooperator": True,
            }
        )
        vals = self._get_dummy_company_subscription_requests_vals()
        subscription_request = self.env["subscription.request"].create(vals)
        partner = subscription_request.partner_id
        # if there are multiple company register number matches, take the one
        # that is a cooperator.
        self.assertEqual(partner, company_partner2)

    def test_create_subscription_with_matching_empty_company_register_number(self):
        company_partner = self.env["res.partner"].create(
            {
                "name": "dummy company",
                "email": "dummycompany@example.net",
                "company_register_number": "",
                "is_company": True,
            }
        )
        vals = self._get_dummy_company_subscription_requests_vals()
        vals["company_register_number"] = ""
        subscription_request = self.env["subscription.request"].create(vals)
        partner = subscription_request.partner_id
        self.assertNotEqual(partner, company_partner)

    def test_create_subscription_with_matching_space_company_register_number(self):
        company_partner = self.env["res.partner"].create(
            {
                "name": "dummy company",
                "email": "dummycompany@example.net",
                "company_register_number": "",
                "is_company": True,
            }
        )
        vals = self._get_dummy_company_subscription_requests_vals()
        vals["company_register_number"] = " "
        subscription_request = self.env["subscription.request"].create(vals)
        partner = subscription_request.partner_id
        self.assertNotEqual(partner, company_partner)

    def test_create_subscription_with_matching_none_company_register_number(self):
        company_partner = self.env["res.partner"].create(
            {
                "name": "dummy company",
                "email": "dummycompany@example.net",
                "is_company": True,
            }
        )
        vals = self._get_dummy_company_subscription_requests_vals()
        del vals["company_register_number"]
        subscription_request = self.env["subscription.request"].create(vals)
        partner = subscription_request.partner_id
        self.assertNotEqual(partner, company_partner)
