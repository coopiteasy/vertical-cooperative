from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ShareLineUpdateInfo(models.TransientModel):
    _name = "share.line.update.info"
    _description = "Share line update info"

    @api.model
    def _get_share_line(self):
        active_id = self.env.context.get("active_id")
        return self.env["share.line"].browse(active_id)

    @api.model
    def _get_effective_date(self):
        share_line = self._get_share_line()

        return share_line.effective_date

    effective_date = fields.Date(
        string="effective date", required=True, default=_get_effective_date
    )
    cooperator = fields.Many2one(related="share_line.partner_id", string="Cooperator")
    share_line = fields.Many2one(
        "share.line", string="Share line", default=_get_share_line
    )

    def update(self):

        line = self.share_line
        cooperator = line.partner_id

        sub_reg = self.env["subscription.register"].search(
            [
                ("partner_id", "=", cooperator.id),
                ("share_product_id", "=", line.share_product_id.id),
                ("quantity", "=", line.share_number),
                ("date", "=", line.effective_date),
            ]
        )
        if sub_reg:
            if len(sub_reg) > 1:
                raise UserError(
                    _(
                        "Error the update return more than one"
                        " subscription register lines."
                    )
                )
            else:
                line.effective_date = self.effective_date
                sub_reg.date = self.effective_date
        return True
