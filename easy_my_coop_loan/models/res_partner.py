# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    loan_line_ids = fields.One2many(
        comodel_name="loan.issue.line",
        inverse_name="partner_id",
        string="Loans",
    )
    is_loaner = fields.Boolean(
        string="Loaner", compute="_compute_is_loaner", store=True
    )

    @api.multi
    @api.depends("loan_line_ids", "loan_line_ids.state")
    def _compute_is_loaner(self):
        for partner in self:
            loans = partner.sudo().loan_line_ids.filtered(
                lambda l: l.state in ["subscribed", "waiting", "paid"]
            )
            partner.is_loaner = bool(loans)
