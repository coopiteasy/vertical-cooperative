# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from odoo.exceptions import AccessError
from odoo.fields import Date
from odoo.tests.common import SavepointCase, users

from .cooperator_test_mixin import CooperatorTestMixin


class CooperatorCase(SavepointCase, CooperatorTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_up_cooperator_test_data()
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        cls.payment_method = cls.env.ref("account.account_payment_method_manual_in")
        cls.share_line = cls.env["share.line"].create(
            {
                "share_product_id": cls.share_x.id,
                "share_number": 2,
                "share_unit_price": 50,
                "partner_id": cls.demo_partner.id,
                "effective_date": datetime.now() - timedelta(days=120),
            }
        )

    @users("user-cooperator")
    def test_put_on_waiting_list(self):
        self.subscription_request_1.put_on_waiting_list()
        self.assertEqual(self.subscription_request_1.state, "waiting")

    @users("user-cooperator")
    def test_validate_subscription_request(self):
        self.subscription_request_1.validate_subscription_request()

        self.assertEqual(self.subscription_request_1.state, "done")
        self.assertTrue(self.subscription_request_1.partner_id)
        self.assertTrue(self.subscription_request_1.partner_id.coop_candidate)
        self.assertFalse(self.subscription_request_1.partner_id.member)
        self.assertEqual(self.subscription_request_1.type, "new")
        self.assertTrue(len(self.subscription_request_1.capital_release_request) >= 1)
        self.assertEqual(
            self.subscription_request_1.capital_release_request.state, "open"
        )
        self.assertTrue(self.subscription_request_1.capital_release_request.sent)

    @users("user-cooperator")
    def test_register_payment_for_capital_release(self):
        self.as_cooperator_user()
        self.subscription_request_1.validate_subscription_request()
        invoice = self.subscription_request_1.capital_release_request
        self.assertEqual(
            invoice.number,
            "SUBJ/{year}/001".format(year=date.today().year),
        )

    def _pay_invoice(self, invoice, payment_date=None):
        ctx = {"active_model": "account.invoice", "active_ids": [invoice.id]}
        register_payments_vals = {
            "journal_id": self.bank_journal.id,
            "payment_method_id": self.payment_method.id,
        }
        if payment_date is not None:
            register_payments_vals["payment_date"] = payment_date
        register_payments = (
            self.env["account.register.payments"]
            .with_context(ctx)
            .create(register_payments_vals)
        )
        register_payments.create_payments()

    @users("user-cooperator")
    def test_register_payment_for_capital_release(self):
        self.subscription_request_1.validate_subscription_request()
        invoice = self.subscription_request_1.capital_release_request

        self._pay_invoice(invoice)
        self.assertEqual(invoice.state, "paid")

        partner = self.subscription_request_1.partner_id
        self.assertFalse(partner.coop_candidate)
        self.assertTrue(partner.member)
        self.assertTrue(partner.share_ids)
        self.assertEqual(partner.effective_date, Date.today())

        share = partner.share_ids[0]
        self.assertEqual(share.share_number, self.subscription_request_1.ordered_parts)
        self.assertEqual(
            share.share_product_id, self.subscription_request_1.share_product_id
        )
        self.assertEqual(share.effective_date, Date.today())

    @users("demo")
    def test_user_access_rules(self):
        user_demo = self.env.ref("base.user_demo")
        # class object was loaded with root user and its rights
        # so we need to reload it with demo user rights
        resquest_as_user = self.subscription_request_1.sudo(user_demo)
        with self.assertRaises(AccessError):
            resquest_as_user.name = "test write request"
        with self.assertRaises(AccessError):
            create_values = self._get_dummy_subscription_requests_vals()
            self.env["subscription.request"].create(create_values)
        with self.assertRaises(AccessError):
            resquest_as_user.unlink()

        share_line_as_user = self.share_line.sudo(user_demo)
        with self.assertRaises(AccessError):
            share_line_as_user.share_number = 3

    @users("user-cooperator")
    def test_cooperator_access_rules(self):
        cooperator_user = self.ref("cooperator.res_users_user_cooperator_demo")
        # cf comment in test_user_access_rules
        resquest_as_cooperator = self.subscription_request_1.sudo(cooperator_user)
        resquest_as_cooperator.name = "test write request"
        create_values = self._get_dummy_subscription_requests_vals()
        create_request = self.env["subscription.request"].create(create_values)
        with self.assertRaises(AccessError):
            create_request.unlink()

        share_line_as_cooperator_user = self.share_line.sudo(cooperator_user)
        share_line_as_cooperator_user.share_number = 3
        with self.assertRaises(AccessError):
            share_line_as_cooperator_user.unlink()

        share_type_as_cooperator_user = self.share_x.sudo(cooperator_user)
        share_type_as_cooperator_user.list_price = 30
        with self.assertRaises(AccessError):
            self.env["product.template"].create(
                {
                    "name": "Part C - Client",
                    "short_name": "Part C",
                    "is_share": True,
                    "list_price": 50,
                }
            )
        with self.assertRaises(AccessError):
            share_type_as_cooperator_user.unlink()

    @users("manager-cooperator")
    def test_cooperator_manager_access_rules(self):
        cooperator_manager = self.ref("cooperator.res_users_manager_cooperator_demo")
        # cf comment in test_user_access_rules
        request_as_cooperator_manager = self.subscription_request_1.sudo(
            cooperator_manager
        )
        request_as_cooperator_manager.name = "test write request"
        create_values = self._get_dummy_subscription_requests_vals()
        create_request = self.env["subscription.request"].create(create_values)
        with self.assertRaises(AccessError):
            create_request.unlink()

        share_type = self.env["product.template"].create(
            {
                "name": "Part C - Client",
                "short_name": "Part C",
                "is_share": True,
                "list_price": 50,
            }
        )
        share_type.list_price = 30
        share_type.unlink()

    def test_compute_is_valid_iban_on_subscription_request(self):
        self.subscription_request_1.iban = False
        self.subscription_request_1.skip_iban_control = False

        # empty iban - don't skip
        self.assertFalse(self.subscription_request_1.is_valid_iban)

        # good iban - don't skip
        self.subscription_request_1.iban = "BE71096123456769"
        self.assertTrue(self.subscription_request_1.is_valid_iban)

        # wrong iban - don't skip
        self.subscription_request_1.iban = "xxxx"
        self.assertFalse(self.subscription_request_1.is_valid_iban)

        # wrong iban - don't skip
        self.subscription_request_1.iban = "BE71096123456760"
        self.assertFalse(self.subscription_request_1.is_valid_iban)

        # wrong iban - skip
        self.subscription_request_1.skip_iban_control = True
        self.assertTrue(self.subscription_request_1.is_valid_iban)

        # empty iban - skip
        self.subscription_request_1.iban = False
        self.assertTrue(self.subscription_request_1.is_valid_iban)

    def _get_dummy_subscription_requests_vals(self):
        return {
            "share_product_id": self.share_y.id,
            "ordered_parts": 2,
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
            "source": "manual",
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
        self.assertEqual(partner.birthdate_date, date(1980, 1, 1))
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
        self.assertEqual(representative.birthdate_date, date(1980, 1, 1))
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
