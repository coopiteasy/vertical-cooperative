# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.exceptions import AccessError
from odoo.fields import Date

from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase


class EMCLoanCase(EMCBaseCase):
    def test_complete_loan_flow(self):

        loan_issue_values = {
            "name": "test loan issue",
            "default_issue": "xx",
            "subscription_start_date": Date.today(),
            "subscription_end_date": Date.today() + timedelta(days=60),
            "user_id": self.ref("easy_my_coop.res_users_manager_emc_demo"),
            "term_date": Date.today() + timedelta(days=600),  # ?
            "gross_rate": 0.03,
            "face_value": 100,
            "minimum_amount": 4000,
            "maximum_amount": 10000,
            "interest_payment": "end",
            "by_company": True,
            "by_individual": True,
            "display_on_website": True,
            "taxes_rate": 0.08,
            "loan_term": 12,
        }

        self.as_emc_manager()
        loan_issue = self.env["loan.issue"].create(loan_issue_values)
        loan_issue.action_confirm()
        loan_issue.action_open()
        loan_issue.action_cancel()
        loan_issue.action_draft()
        loan_issue.action_open()

    def test_emc_user_cannot_manage_loan_issue(self):
        self.as_emc_user()

        loan_issue_values = {
            "name": "test loan issue",
            "default_issue": True,
            "user_id": self.ref("easy_my_coop.res_users_manager_emc_demo"),
            "subscription_start_date": Date.today(),
            "subscription_end_date": Date.today() + timedelta(days=60),
            "term_date": Date.today() + timedelta(days=600),  # ?
            "gross_rate": 0.03,
            "face_value": 100,
            "minimum_amount": 2000,
            "maximum_amount": 10000,  # ?
            "interest_payment": "end",
            "by_company": True,
            "by_individual": True,
            "display_on_website": True,
            "taxes_rate": 0.08,
        }

        with self.assertRaises(AccessError):
            self.env["loan.issue"].create(loan_issue_values)

        loan_issue = self.browse_ref("easy_my_coop_loan.loan_issue_1_demo")

        with self.assertRaises(AccessError):
            loan_issue.name = "some name"
        with self.assertRaises(AccessError):
            loan_issue.action_confirm()
        with self.assertRaises(AccessError):
            loan_issue.action_open()
        with self.assertRaises(AccessError):
            loan_issue.action_cancel()
        with self.assertRaises(AccessError):
            loan_issue.action_draft()
        with self.assertRaises(AccessError):
            loan_issue.action_open()

        self.as_emc_manager()
        loan_issue_manager = self.browse_ref("easy_my_coop_loan.loan_issue_1_demo")
        loan_issue_manager.action_confirm()
        loan_issue_manager.action_open()

        self.as_emc_user()
        line = self.env["loan.issue.line"].create(
            {
                "loan_issue_id": loan_issue.id,
                "quantity": 3,
                "partner_id": self.browse_ref(
                    "easy_my_coop.res_partner_cooperator_4_demo"
                ).id,
            }
        )
        line.action_validate()
        line.action_cancel()
        line.action_draft()
        line.action_validate()
        line.action_request_payment()
        line.action_paid()

        loan_issue.compute_loan_interest()
