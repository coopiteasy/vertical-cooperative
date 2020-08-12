# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class EMCBaseCase(common.TransactionCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)

    def _chart_template_create(self):
        transfer_account_id = self.env["account.account.template"].create(
            {
                "code": "000",
                "name": "Liquidity Transfers",
                "reconcile": True,
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
            }
        )
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
        transfer_account_id.update({"chart_template_id": self.chart.id})
        self.env["ir.model.data"].create(
            {
                "res_id": transfer_account_id.id,
                "model": transfer_account_id._name,
                "name": "Liquidity Transfers",
            }
        )
        act = self.env["account.account.template"].create(
            {
                "code": "001",
                "name": "Expenses",
                "user_type_id": self.env.ref(
                    "account.data_account_type_expenses"
                ).id,
                "chart_template_id": self.chart.id,
                "reconcile": True,
            }
        )
        self.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "expenses"}
        )
        act = self.env["account.account.template"].create(
            {
                "code": "002",
                "name": "Product Sales",
                "user_type_id": self.env.ref(
                    "account.data_account_type_revenue"
                ).id,
                "chart_template_id": self.chart.id,
                "reconcile": True,
            }
        )
        self.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "sales"}
        )
        act = self.env["account.account.template"].create(
            {
                "code": "003",
                "name": "Account Receivable",
                "user_type_id": self.env.ref(
                    "account.data_account_type_receivable"
                ).id,
                "chart_template_id": self.chart.id,
                "reconcile": True,
            }
        )
        self.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "receivable"}
        )
        act = self.env["account.account.template"].create(
            {
                "code": "004",
                "name": "Account Payable",
                "user_type_id": self.env.ref(
                    "account.data_account_type_payable"
                ).id,
                "chart_template_id": self.chart.id,
                "reconcile": True,
            }
        )
        self.env["ir.model.data"].create(
            {"res_id": act.id, "model": act._name, "name": "payable"}
        )

    def _add_chart_of_accounts(self):
        self.company = self.env.user.company_id
        self.chart.try_loading_for_current_company()
        self.revenue = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        self.expense = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_expenses").id,
                )
            ],
            limit=1,
        )
        self.receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        self.payable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_payable").id,
                )
            ],
            limit=1,
        )
        self.equity_account = self.env.ref("easy_my_coop.account_equity_demo")
        self.cooperator_account = self.env.ref(
            "easy_my_coop.account_cooperator_demo"
        )
        return True

    def _journals_setup(self):
        self.subscription_journal = self.env.ref(
            "easy_my_coop.subscription_journal"
        )
        self.subscription_journal.write(
            {
                "default_debit_account_id": self.equity_account.id,
                "default_credit_account_id": self.equity_account.id,
            }
        )
        self.bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        return True

    def setUp(self):
        super(EMCBaseCase, self).setUp()
        self._chart_template_create()
        self._add_chart_of_accounts()
        self._journals_setup()

    def as_user(self):
        self.uid = self.ref("base.user_demo")

    def as_emc_user(self):
        self.uid = self.ref("easy_my_coop.res_users_user_emc_demo")

    def as_emc_manager(self):
        self.uid = self.ref("easy_my_coop.res_users_manager_emc_demo")
