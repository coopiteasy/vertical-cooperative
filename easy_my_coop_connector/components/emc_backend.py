# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
import logging

import requests
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied, Warning as UserError

_logger = logging.getLogger(__name__)


class EMCBackend(models.Model):
    _name = "emc.backend"
    _description = "EMC Backend"

    name = fields.Char(string="Name", required=True)
    location = fields.Char(string="URL")
    api_key = fields.Char(string="API Key")
    description = fields.Text(string="Description", required=False)
    active = fields.Boolean(string="active", default=True)

    @api.model
    def get_backend(self):
        backend = self.env["emc.backend"].search([("active", "=", True)])
        try:
            backend.ensure_one()
        except ValueError as e:
            _logger.error(
                "One and only one backend is allowed for the Easy My Coop " "connector."
            )
            raise e
        return backend

    @api.multi
    def http_get(self, url, params=None, headers=None):
        self.ensure_one()
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = self.location + url

        _logger.info("GET to {} w/ params {}".format(url, params))
        response = requests.get(url, params=params, headers=headers)
        self._log_emc_api_call(response)
        return response

    @api.multi
    def http_get_content(self, url, params=None, headers=None):
        self.ensure_one()
        response = self.http_get(url, params=params, headers=headers)
        return self._process_response(response)

    @api.multi
    def http_post(self, url, data, headers=None):
        self.ensure_one()
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = self.location + url

        _logger.info("POST to %s" % url)
        response = requests.post(url, json=data, headers=headers)
        self._log_emc_api_call(response)
        return response

    def http_post_content(self, url, data, headers=None):
        self.ensure_one()
        response = self.http_post(url, data, headers=headers)
        return self._process_response(response)

    @api.multi
    def http_put(self, url, data, headers=None):
        self.ensure_one()
        headers = self._add_api_key(headers)
        if url.startswith("/"):
            url = self.location + url

        _logger.info("PUT to %s" % url)
        response = requests.put(url, json=data, headers=headers)
        self._log_emc_api_call(response)
        return response

    def http_put_content(self, url, data, headers=None):
        self.ensure_one()
        response = self.http_put(url, data, headers=headers)
        return self._process_response(response)

    @api.multi
    def _add_api_key(self, headers):
        self.ensure_one()
        key_dict = {"API-KEY": self.api_key}
        if headers:
            headers.update(key_dict)
        else:
            headers = key_dict
        return headers

    def _process_response(self, response):
        if response.status_code == 200:
            content = response.content.decode("utf-8")
            return json.loads(content)
        elif response.status_code == 400:
            content = response.content.decode("utf-8")
            raise BadRequest("%s" % content)
        elif response.status_code == 403:
            raise AccessDenied(_("You are not allowed to access this resource"))
        elif response.status_code == 404:
            raise NotFound(_("Resource not found %s on server" % response.status_code))
        else:  # 500 et al.
            content = response.content.decode("utf-8")
            raise InternalServerError(_("%s" % content))

    def _log_emc_api_call(self, response):
        request = response.request
        # only admin can create emc.api.log
        self.env["emc.api.log"].create(
            {
                "datetime": fields.datetime.now(),
                "method": request.method,
                "path": request.url,
                "headers": request.headers,
                "payload": request.body,
                "response": response.content,
                "status": response.status_code,
            }
        )

    @api.multi
    def action_ping(self):
        self.ensure_one()
        url = self.location + "/api/ping/test"
        # todo ping as authentificated user
        try:
            response = requests.get(url)
        except Exception as e:
            _logger.error(e)
            raise UserError(_("Failed to connect to backend: %s" % str(e)))

        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
            raise UserError(_("Success: %s") % content["message"])
        else:
            raise UserError(
                _("Failed to connect to backend: %s" % str(response.content))
            )
