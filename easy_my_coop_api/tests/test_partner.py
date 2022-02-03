# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from werkzeug.exceptions import NotFound

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext

from .common import BaseEMCRestCase

EXPECTED_PARTNER_DICT = {
    "firstname": "Virginie",
    "lastname": "Leloup",
    "email": "virginie@demo.net",
    "address": {
        "street": "Avenue des Dessus-de-Livres, 2",
        "zip_code": "5101",
        "city": "Namur (Loyers)",
        "country": "BE",
    },
    "birthdate": None,
    "gender": None,
    "lang": "en_US",
    "phone": "0456765436",
    "is_company": False,
    "iban": "FR76 1180 8009 1012 3456 7890 147",
    "data_policy_approved": False,
    "financial_risk_approved": False,
    "generic_rules_approved": False,
    "internal_rules_approved": False,
}

EXPECTED_COMPANY_DICT = {
    "firstname": False,
    "lastname": "Rochdale Cooperative",
    "email": "info@rochdale.coop",
    "address": {
        "street": "Avenue de la coopération, 2",
        "zip_code": "5101",
        "city": "Namur",
        "country": "BE",
    },
    "birthdate": None,
    "gender": None,
    "lang": "en_US",
    "phone": "0456788436",
    "is_company": True,
    "iban": None,
    "data_policy_approved": True,
    "financial_risk_approved": True,
    "generic_rules_approved": True,
    "internal_rules_approved": True,
}


class TestPartnerService(BaseEMCRestCase):
    def setUp(self):
        super().setUp()
        collection = _PseudoCollection("emc.services", self.env)
        emc_services_env = WorkContext(
            model_name="rest.service.registration", collection=collection
        )

        self.partner_service = emc_services_env.component(usage="partner")
        belgium = self.env["res.country"].search([("code", "=", "BE")])

        self.contact_partner = self.env["res.partner"].create(
            {
                "firstname": "Virginie",
                "lastname": "Leloup",
                "email": "virginie@demo.net",
                "street": "Avenue des Dessus-de-Livres, 2",
                "zip": "5101",
                "city": "Namur (Loyers)",
                "country_id": belgium.id,
                "birthdate_date": False,
                "gender": False,
                "lang": "en_US",
                "phone": "0456765436",
                "is_company": False,
                "data_policy_approved": False,
                "financial_risk_approved": False,
                "generic_rules_approved": False,
                "internal_rules_approved": False,
            }
        )
        self.env["res.partner.bank"].sudo().create(
            {
                "partner_id": self.contact_partner.id,
                "acc_number": "FR76 1180 8009 1012 3456 7890 147",
            }
        )
        self.contact_partner.timestamp_export()
        self.expected_contact_partner_dict = EXPECTED_PARTNER_DICT.copy()
        self.expected_contact_partner_dict[
            "id"
        ] = self.contact_partner.get_api_external_id()

    def test_get_partner(self):
        partner = self.contact_partner
        service_response = self.partner_service.get(partner.get_api_external_id())
        self.assertEquals(self.expected_contact_partner_dict, service_response)

    def test_get_company_partner(self):
        belgium = self.env["res.country"].search([("code", "=", "BE")])
        company_partner = self.env["res.partner"].create(
            {
                "name": "Rochdale Cooperative",
                "email": "info@rochdale.coop",
                "street": "Avenue de la coopération, 2",
                "zip": "5101",
                "city": "Namur",
                "country_id": belgium.id,
                "birthdate_date": False,
                "gender": False,
                "lang": "en_US",
                "phone": "0456788436",
                "is_company": True,
                "data_policy_approved": True,
                "financial_risk_approved": True,
                "generic_rules_approved": True,
                "internal_rules_approved": True,
            }
        )
        company_partner.timestamp_export()
        self.contact_partner.parent_id = company_partner

        company_external_id = company_partner.get_api_external_id()
        expected_contact_dict = self.expected_contact_partner_dict.copy()
        expected_contact_dict.update(
            {"company": {"id": company_external_id, "name": company_partner.name}}
        )

        service_response = self.partner_service.get(
            self.contact_partner.get_api_external_id()
        )
        self.assertEquals(expected_contact_dict, service_response)

        service_response = self.partner_service.get(
            company_partner.get_api_external_id()
        )
        expected_company_dict = EXPECTED_COMPANY_DICT.copy()
        expected_company_dict["id"] = company_external_id
        self.assertEquals(expected_company_dict, service_response)

    def test_get_partner_not_found(self):
        unknown_external_id = 987654
        assert not self.env["res.partner"].search(
            [("_api_external_id", "=", unknown_external_id)]
        )
        with self.assertRaises(NotFound):
            self.partner_service.get(unknown_external_id)
