from odoo import api, models


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode="refund"):
        result = super(AccountInvoiceRefund, self).compute_refund(mode)
        context = dict(self._context or {})

        inv = self.env["account.invoice"].browse(context.get("active_ids"))
        if inv.release_capital_request:
            domain = result["domain"]
            t = ("release_capital_request", "=", True)
            out = [t if e[0] == t[0] else e for e in domain]
            result["domain"] = out
        return result
