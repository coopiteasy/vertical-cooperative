# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EMCBinding(models.AbstractModel):
    _name = "emc.binding"
    _description = "EMC Binding (abstract)"

    backend_id = fields.Many2one(
        comodel_name="emc.backend", string="EMC Backend", ondelete="cascade"
    )
    external_id = fields.Integer(string="ID in Platform", index=True)

    # internal_id = fields.Many2one(  # implement in concrete model
    #     comodel_name="bound model",
    #     string="Internal ID",
    #     required=True,
    #     ondelete="cascade",
    # )

    @api.model
    def search_binding(self, backend, external_id):
        return self.search(
            [
                ("backend_id", "=", backend.id),
                ("external_id", "=", external_id),
            ]
        )


class SubscriptionRequestBinding(models.Model):
    _name = "emc.binding.subscription.request"
    _inherit = "emc.binding"

    internal_id = fields.Many2one(
        comodel_name="subscription.request",
        string="Internal ID",
        required=True,
        ondelete="cascade",
    )


class ProductTemplateBinding(models.Model):
    _name = "emc.binding.product.template"
    _inherit = "emc.binding"

    internal_id = fields.Many2one(
        comodel_name="product.template",
        string="Internal ID",
        domain="[('is_share', '=', True)]",
        required=True,
        ondelete="cascade",
    )


class AccountInvoiceBinding(models.Model):
    _name = "emc.binding.account.invoice"
    _inherit = "emc.binding"

    internal_id = fields.Many2one(
        comodel_name="account.invoice",
        string="Internal ID",
        required=True,
        ondelete="cascade",
    )


class AccountPaymentBinding(models.Model):
    _name = "emc.binding.account.payment"
    _inherit = "emc.binding"

    internal_id = fields.Many2one(
        comodel_name="account.payment",
        string="Internal ID",
        required=True,
        ondelete="cascade",
    )


class AccountJournalBinding(models.Model):
    _name = "emc.binding.account.journal"
    _inherit = "emc.binding"

    internal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Internal ID",
        required=True,
        ondelete="cascade",
    )


class AccountAccountBinding(models.Model):
    _name = "emc.binding.account.account"
    _inherit = "emc.binding"

    internal_id = fields.Many2one(
        comodel_name="account.account",
        string="Internal ID",
        required=True,
        ondelete="cascade",
    )
