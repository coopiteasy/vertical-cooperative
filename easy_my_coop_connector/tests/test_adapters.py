# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.easy_my_coop.tests.test_base import EMCBaseCase

from ..components.abstract_emc_adapter import AbstractEMCAdapter


class EMCAdapterCase(EMCBaseCase):
    def test_get_url(self):
        adapter = AbstractEMCAdapter(backend=None, record=None)
        adapter._service = "test-service"
        self.assertEquals(adapter._get_url(), "/api/test-service")
        self.assertEquals(adapter._get_url(["1"]), "/api/test-service/1")
        self.assertEquals(
            adapter._get_url(["1", "update"]), "/api/test-service/1/update"
        )
