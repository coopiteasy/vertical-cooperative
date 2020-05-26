# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import uuid

from odoo import api, fields, models


class AuthApiKey(models.Model):
    _inherit = "auth.api.key"

    def _default_key(self):
        return uuid.uuid4()

    # overloaded fields
    # required is set to false to allow for a computed field,
    # it will always be set.
    name = fields.Char(required=False, compute="_compute_name", store=True)
    key = fields.Char(default=_default_key)

    @api.multi
    @api.depends("user_id")
    def _compute_name(self):
        for key in self:
            if key.user_id:
                now = fields.Datetime.now()

                key.name = "{login}-{now}".format(
                    now=fields.Datetime.to_string(now), login=key.user_id.login
                )
            else:
                key.name = "no-user"
