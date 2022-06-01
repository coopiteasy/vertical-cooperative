# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class EMCAPILog(models.Model):
    _name = "emc.api.log"
    _description = "Logs call to EMC API"
    _order = "datetime desc"

    datetime = fields.Datetime(
        default=lambda _: fields.Datetime.now(),
        required=True,
        readonly=True,
    )
    method = fields.Char(required=True, readonly=True)
    path = fields.Char(required=True, readonly=True)
    headers = fields.Text(readonly=True)
    payload = fields.Text(readonly=True)
    response = fields.Text(readonly=True)
    status = fields.Char(required=True, readonly=True)
    ip = fields.Char(
        string="IP",
        required=False,  # todo change
        readonly=True,
    )
