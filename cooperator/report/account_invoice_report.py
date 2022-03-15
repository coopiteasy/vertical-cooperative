from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    release_capital_request = fields.Boolean(string="Release capital request")

    def _select(self):
        return (
            super(AccountInvoiceReport, self)._select()
            + ", sub.release_capital_request as release_capital_request"
        )

    def _sub_select(self):
        return (
            super(AccountInvoiceReport, self)._sub_select()
            + ", ai.release_capital_request as release_capital_request"
        )
