# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

from werkzeug.exceptions import BadRequest, NotFound

from odoo import _

from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import AbstractComponent


class BaseRestService(AbstractComponent):
    _name = "emc.rest.service"
    _inherit = "base.rest.service"
    _collection = "emc.services"
    _usage = "set in concrete class"
    _model = "set in concrete class"
    _description = """
        Base Rest Services
    """

    def _one_to_many_to_dict(self, record):
        if record:
            return {"id": record.get_api_external_id(), "name": record.name}
        else:
            return {}

    def _or_none(self, value):
        if value:
            return value
        else:
            return None

    def _browse_record(self, _id):
        """
        :param _id: external id
        :return: record of model _model for given external id
        """
        record = self.env[self._model].search([("_api_external_id", "=", _id)])
        if not record:
            raise wrapJsonException(
                NotFound(_("No %s record for id %s") % (self._usage, _id))
            )
        return record

    def _get_country(self, code):
        country = self.env["res.country"].search([("code", "=", code)])
        if country:
            return country
        else:
            raise wrapJsonException(BadRequest(_("No country for isocode %s") % code))

    # If get, search, update, create or delete are defined
    # in the service, the route is opened in the controller.
    # therefore we put common code in _<method>.

    def _get(self, _id):
        """
        :param _id: the external id of the resource to get
        :return: a dictionary validated by the return get schema for the
            corresponding model.
        """
        record = self._browse_record(_id)
        return self._to_dict(record)

    def _update(self, _id, **params):
        """
        Updates the record for id _id and model _model
        :param _id: the external id of the resource to update
        :param params: a dictionary validated by the update schema
            for the corresponding model
        :return: a dictionary validated by the return get schema for the
            corresponding model.
        """
        record = self._browse_record(_id)
        params = self._prepare_update(params)
        # need sudo to write on api type records
        record.sudo().write(params)
        return self._to_dict(record)

    def _to_dict(self, sr):
        raise NotImplementedError

    def _prepare_update(self, params):
        raise NotImplementedError
