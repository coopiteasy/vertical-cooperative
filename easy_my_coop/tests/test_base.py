# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class EMCBaseCase(common.TransactionCase):
    def setUp(self):
        super(EMCBaseCase, self).setUp()
        # todo set from demo data
        user = self.env["res.users"].browse(self.uid)
        cooperator_account = self.ref("easy_my_coop.account_cooperator_demo")
        user.company_id.property_cooperator_account = cooperator_account

    def as_user(self):
        self.uid = self.ref("base.user_demo")

    def as_emc_user(self):
        self.uid = self.ref("easy_my_coop.res_users_user_emc_demo")

    def as_emc_manager(self):
        self.uid = self.ref("easy_my_coop.res_users_manager_emc_demo")
