# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

import logging

from werkzeug.exceptions import NotFound

from odoo import _
from odoo.fields import Date

from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class ResPartnerService(Component):
    _name = "res.partner.service"
    _inherit = "emc.rest.service"
    _usage = "partner"
    _model = "res.partner"
    _description = """
        Partner Services
    """

    def get(self, _id):
        partner = self.env["res.partner"].search([("_api_external_id", "=", _id)])
        if partner:
            return self._to_dict(partner)
        else:
            raise wrapJsonException(NotFound(_("No partner found for id %s") % _id))

    def search(self, date_from=None, date_to=None):
        raise NotImplementedError

    def update(self, _id, **params):
        raise NotImplementedError

    def _to_dict(self, partner):
        partner.ensure_one()
        partner.timestamp_export()

        if partner.bank_ids:
            bank_accounts = partner.bank_ids.sorted(
                lambda ba: ba.create_date, reverse=True
            )
            iban = bank_accounts[0].acc_number
        else:
            iban = False

        partner_dict = {
            "id": partner.get_api_external_id(),
            "firstname": partner.firstname,
            "lastname": partner.lastname,
            "email": partner.email,
            "address": {
                "street": partner.street,
                "zip_code": partner.zip,
                "city": partner.city,
                "country": partner.country_id.code,
            },
            "birthdate": self._or_none(Date.to_string(partner.birthdate_date)),
            "gender": self._or_none(partner.gender),
            "lang": partner.lang,
            "phone": self._or_none(partner.phone),
            "is_company": partner.is_company,
            "iban": self._or_none(iban),
            "data_policy_approved": partner.data_policy_approved,
            "financial_risk_approved": partner.financial_risk_approved,
            "generic_rules_approved": partner.generic_rules_approved,
            "internal_rules_approved": partner.internal_rules_approved,
        }

        if partner.parent_id:
            company = partner.parent_id
            company.timestamp_export()
            company_dict = {
                "id": company.get_api_external_id(),
                "name": company.name,
            }
            partner_dict.update({"company": company_dict})

        return partner_dict

    def _validator_get(self):
        return schemas.S_PARTNER_GET

    def _validator_return_get(self):
        return schemas.S_PARTNER_RETURN_GET
