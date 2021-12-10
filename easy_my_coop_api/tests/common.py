# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import json

import requests
from lxml import html

import odoo

from odoo.addons.base_rest.tests.common import BaseRestCase

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCase(BaseRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.AuthApiKey = cls.env["auth.api.key"]
        cls.api_key_test = cls.env.ref("easy_my_coop_api.auth_api_key_manager_emc_demo")
        cls._chart_template_create()
        cls._add_chart_of_accounts()
        cls._journals_setup()

    def setUp(self):
        super().setUp()
        # tests are run as res_users_manager_emc_demo with
        #   emc manager access rights
        self.uid = self.ref("easy_my_coop.res_users_manager_emc_demo")
        self.session = requests.Session()

    @classmethod
    def _chart_template_create(cls):
        transfer_account_id = cls.env["account.account.template"].create(
            {
                "code": "000",
                "name": "Liquidity Transfers",
                "reconcile": True,
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
            }
        )
        cls.chart = cls.env["account.chart.template"].create(
            {
                "name": "Test COA",
                "code_digits": 4,
                "bank_account_code_prefix": 1014,
                "cash_account_code_prefix": 1014,
                "currency_id": cls.env.ref("base.USD").id,
                "transfer_account_code_prefix": "000",
            }
        )
        transfer_account_id.update({"chart_template_id": cls.chart.id})
        cls.env["ir.model.data"].create(
            {
                "res_id": transfer_account_id.id,
                "model": transfer_account_id._name,
                "name": "Liquidity Transfers",
            }
        )
        act = cls.env["account.account.template"].create(
            {
                "code": "001",
                "name": "Expenses",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "chart_template_id": cls.chart.id,
                "reconcile": True,
            }
        )
        cls.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "expenses"}
        )
        act = cls.env["account.account.template"].create(
            {
                "code": "002",
                "name": "Product Sales",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
                "chart_template_id": cls.chart.id,
                "reconcile": True,
            }
        )
        cls.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "sales"}
        )
        act = cls.env["account.account.template"].create(
            {
                "code": "003",
                "name": "Account Receivable",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "chart_template_id": cls.chart.id,
                "reconcile": True,
            }
        )
        cls.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "receivable"}
        )
        act = cls.env["account.account.template"].create(
            {
                "code": "004",
                "name": "Account Payable",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "chart_template_id": cls.chart.id,
                "reconcile": True,
            }
        )
        cls.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "payable"}
        )

    @classmethod
    def _add_chart_of_accounts(cls):
        cls.company = cls.env.user.company_id
        cls.chart.try_loading_for_current_company()
        cls.revenue = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        cls.expense = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_expenses").id,
                )
            ],
            limit=1,
        )
        cls.receivable = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        cls.payable = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_payable").id,
                )
            ],
            limit=1,
        )
        cls.equity_account = cls.env.ref("easy_my_coop.account_equity_demo")
        cls.cooperator_account = cls.env.ref("easy_my_coop.account_cooperator_demo")
        return True

    @classmethod
    def _journals_setup(cls):
        cls.subscription_journal = cls.env.ref("easy_my_coop.subscription_journal")
        cls.subscription_journal.write(
            {
                "default_debit_account_id": cls.equity_account.id,
                "default_credit_account_id": cls.equity_account.id,
            }
        )
        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        return True

    def _add_api_key(self, headers):
        key_dict = {"API-KEY": self.api_key_test.key}
        if headers:
            headers.update(key_dict)
        else:
            headers = key_dict
        return headers

    def http_get(self, url, headers=None):
        # api is called by res_users_manager_emc_demo with
        #   emc manager access rights
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)

        return self.session.get(url, headers=headers)

    def http_get_content(self, route, headers=None):
        response = self.http_get(route, headers=headers)
        self.assertEquals(response.status_code, 200)
        content = response.content.decode("utf-8")
        return json.loads(content)

    def http_post(self, url, data, headers=None):
        # api is called by res_users_manager_emc_demo with
        #   emc manager access rights
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)

        return self.session.post(url, json=data, headers=headers)

    @staticmethod
    def html_doc(response):
        """Get an HTML LXML document."""
        return html.fromstring(response.content)

    def login(self, login, password):
        url = "/web/login"
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)

        doc = self.html_doc(response)
        token = doc.xpath("//input[@name='csrf_token']")[0].get("value")

        response = self.http_post(
            url=url,
            data={"login": login, "password": password, "csrf_token": token},
        )
        self.assertEquals(response.status_code, 200)
        return response
