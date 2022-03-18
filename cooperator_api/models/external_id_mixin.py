# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError

from odoo import api, fields, models
from odoo.fields import Datetime


class ExternalIdMixin(models.AbstractModel):
    _name = "external.id.mixin"
    _description = "External ID Mixin"

    _sql_constraints = [
        (
            "_api_external_id_uniq",
            "unique(_api_external_id)",
            "API External ID must be unique!",
        )
    ]

    # do not access directly, always use get_api_external_id method
    _api_external_id = fields.Integer(
        string="External ID", index=True, required=False, copy=False
    )
    external_id_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="External ID Sequence",
        required=False,
        copy=False,
    )
    first_api_export_date = fields.Datetime(
        string="First API Export Date", required=False, copy=False
    )
    last_api_export_date = fields.Datetime(
        string="Last API Export Date", required=False, copy=False
    )
    external_id_generated = fields.Boolean(
        string="External ID Generated",
        default=False,
        copy=False,
    )

    @api.multi
    def timestamp_export(self):
        sudo_self = self.sudo()
        sudo_self.write({"last_api_export_date": Datetime.now()})
        sudo_self.search([("first_api_export_date", "=", False)]).write(
            {"first_api_export_date": Datetime.now()}
        )

    @api.multi
    def set_external_sequence(self):
        self.ensure_one()
        code = "%s.external.id" % self._name
        Sequence = self.env["ir.sequence"]
        # check if code was created for that model
        sequence = Sequence.search([("code", "=", code)])
        if not sequence:
            sequence = Sequence.sudo().create(
                {"name": code, "code": code, "number_next": 100}
            )

        self.sudo().write({"external_id_sequence_id": sequence.id})
        return True

    @api.multi
    def get_api_external_id(self):
        self.ensure_one()
        if not self.external_id_sequence_id:
            self.set_external_sequence()
        if not self._api_external_id:
            # pass already allocated ids
            n = 100
            while True:
                try:
                    next_id = self.external_id_sequence_id._next()
                    self.sudo().write(
                        {
                            "_api_external_id": next_id,
                            "external_id_generated": True,
                        }
                    )
                    break
                except IntegrityError as e:
                    if n > 0:
                        n -= 1
                        continue
                    else:
                        raise e
        return self._api_external_id


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "external.id.mixin"]


class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "external.id.mixin"]


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ["account.journal", "external.id.mixin"]


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "external.id.mixin"]


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ["account.payment", "external.id.mixin"]


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "external.id.mixin"]
