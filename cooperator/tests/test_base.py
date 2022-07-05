# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class CooperatorBaseCase(common.TransactionCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)

    def _create_account_template(self, code, name, user_type_ref, chart):
        act = self.env["account.account.template"].create(
            {
                "code": code,
                "name": name,
                "user_type_id": self.env.ref(user_type_ref).id,
                "chart_template_id": chart.id,
                "reconcile": True,
            }
        )
        data_name = ("demo %s data" % name).replace(" ", "_")
        self.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": data_name}
        )
        return act

    def _chart_template_create(self):
        self.chart = self.env["account.chart.template"].create(
            {
                "name": "Test COA",
                "code_digits": 4,
                "bank_account_code_prefix": 1014,
                "cash_account_code_prefix": 1014,
                "currency_id": self.env.ref("base.USD").id,
                "transfer_account_code_prefix": "000",
            }
        )
        self._create_account_template(
            "000",
            "Liquidity Transfers",
            "account.data_account_type_current_assets",
            self.chart,
        )
        self._create_account_template(
            "001",
            "Expenses",
            "account.data_account_type_expenses",
            self.chart,
        )
        self._create_account_template(
            "002",
            "Product Sales",
            "account.data_account_type_revenue",
            self.chart,
        )
        self._create_account_template(
            "003",
            "Account Receivable",
            "account.data_account_type_receivable",
            self.chart,
        )
        self._create_account_template(
            "004",
            "Account Payable",
            "account.data_account_type_payable",
            self.chart,
        )
        self._create_account_template(
            "41610",
            "Cooperator Test Account",
            "account.data_account_type_receivable",
            self.chart,
        )
        self._create_account_template(
            "100911",
            "Equity Test Account",
            "account.data_account_type_equity",
            self.chart,
        )

    def _add_chart_of_accounts(self):
        self.company = self.env.company
        self.chart.try_loading()
        account_obj = self.env["account.account"]
        self.expense = account_obj.search(
            [("code", "=", "0010")],
        )
        self.receivable = account_obj.search(
            [("code", "=", "0030")],
        )
        self.payable = account_obj.search(
            [("code", "=", "0040")],
        )
        self.cooperator_account = account_obj.search(
            [("code", "=", "41610")],
        )
        self.equity_account = account_obj.search(
            [("code", "=", "100911")],
        )

        return True

    def _journals_setup(self):
        self.subscription_journal = self.env["account.journal"].create(
            {
                "name": "Subscription Journal (test)",
                "code": "SUBR",
                "type": "sale",
                "payment_debit_account_id": self.equity_account.id,
                "payment_credit_account_id": self.equity_account.id,
            }
        )
        self.bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        return True

    def setUp(self):
        super().setUp()
        self._chart_template_create()
        self._add_chart_of_accounts()
        self._journals_setup()

    def as_user(self):
        self.uid = self.ref("base.user_demo")

    def as_cooperator_user(self):
        self.uid = self.ref("cooperator.res_users_user_cooperator_demo")

    def as_cooperator_manager(self):
        self.uid = self.ref("cooperator.res_users_manager_cooperator_demo")
