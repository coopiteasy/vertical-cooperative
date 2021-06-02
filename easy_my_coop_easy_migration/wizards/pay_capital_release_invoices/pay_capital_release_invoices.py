from odoo import api, models, fields
from odoo.addons.queue_job.job import job


class PayCapitalReleaseInvoices(models.TransientModel):
    _name = "pay.capital.release.invoices"

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

    def pay(self):
        self.with_delay()._create_payments()

    @job
    def _create_payments(self):
        capital_release_invoices = self.env["account.invoice"].search([
            ("state", "=", "open"),
            ("subscription_request", "!=", None),
            ("subscription_request.migrated_cooperator_register_number", "!=", None),
        ]).sorted(lambda i: i.subscription_request.migrated_cooperator_register_number)

        self.AccountRegisterPaymentWizard = self.env["account.register.payments"]

        self.account_payment_method = self.env.ref("account.account_payment_method_manual_in")

        for cs_invoice in capital_release_invoices:
            wizard = self.AccountRegisterPaymentWizard.with_context({
                "active_model": "account.invoice",
                "active_ids": [cs_invoice.id]
            }).create({
                "payment_date": cs_invoice.subscription_request.capital_release_request_date,
                "payment_method_id": self.account_payment_method.id,
                "journal_id": self.journal_id.id,
            })
            wizard.create_payments()
