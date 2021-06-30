import logging
from odoo import api, models, fields
from odoo.addons.queue_job.job import job

log = logging.getLogger(__name__)


class PayCapitalReleaseInvoices(models.TransientModel):
    _name = "pay.capital.release.invoices"

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

    def pay(self):
        self.with_delay()._create_payments()

    @job
    def _create_payments(self):
        log.info("Preparing data to create payments...")
        capital_release_invoices = self.env["account.invoice"].search([
            ("state", "=", "open"),
            ("subscription_request", "!=", None),
            ("subscription_request.migrated_cooperator_register_number", "!=", None),
        ]).sorted(lambda i: i.subscription_request.migrated_cooperator_register_number)

        self.AccountRegisterPaymentWizard = self.env["account.register.payments"]

        self.account_payment_method = self.env.ref("account.account_payment_method_manual_in")

        log.info("Starting to create payments")
        for cs_invoice in capital_release_invoices:
            log.info("Creating payment for invoice {}".format(cs_invoice.invoice_number))
            wizard = self.AccountRegisterPaymentWizard.with_context({
                "active_model": "account.invoice",
                "active_ids": [cs_invoice.id]
            }).create({
                "payment_date": cs_invoice.subscription_request.capital_release_request_date,
                "payment_method_id": self.account_payment_method.id,
                "journal_id": self.journal_id.id,
            })
            try:
                wizard.create_payments()
                self.env.cr.commit()
            except Exception as error:
                self.env.cr.commit()
                raise error
            log.info("Payments created for invoice {}".format(cs_invoice.invoice_number))

