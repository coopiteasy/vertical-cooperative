import logging

from odoo import fields, models

from odoo.addons.queue_job.job import job

log = logging.getLogger(__name__)


class PayCapitalReleaseInvoices(models.TransientModel):
    _name = "pay.capital.release.invoices"

    journal_id = fields.Many2one(
        "account.journal",
        string="Payment Journal",
        required=True,
        domain=[("type", "in", ("bank", "cash"))],
    )

    def pay(self):
        self.with_delay()._create_payments()

    @job
    def _create_payments(self):
        log.info("Preparing data to create payments...")
        capital_release_invoices = (
            self.env["account.invoice"]
            .search(
                [
                    ("state", "=", "open"),
                    ("subscription_request", "!=", False),
                    (
                        "subscription_request.imported_cooperator_register_number",
                        "!=",
                        False,
                    ),
                ]
            )
            .sorted(
                lambda i: i.subscription_request.imported_cooperator_register_number
            )
        )

        self.AccountRegisterPaymentWizard = self.env["account.register.payments"]

        self.account_payment_method = self.env.ref(
            "account.account_payment_method_manual_in"
        )

        log.info("Starting to create payments")
        for cr_invoice in capital_release_invoices:
            log.info(
                "Creating payment for invoice {}".format(cr_invoice.invoice_number)
            )
            wizard = self.AccountRegisterPaymentWizard.with_context(
                {"active_model": "account.invoice", "active_ids": [cr_invoice.id]}
            ).create(
                {
                    "payment_date": cr_invoice.subscription_request.capital_release_request_date,  # noqa
                    "payment_method_id": self.account_payment_method.id,
                    "journal_id": self.journal_id.id,
                }
            )
            # Why are we forcing the commit?
            # We can commit the transaction here because this method is a
            # job, and we want to save the changes done.
            # Then, when we requeue this job, it
            # continues from the last capital release invoice without payments.
            wizard.create_payments()
            self.env.cr.commit()
            log.info(
                "Payments created for invoice {}".format(cr_invoice.invoice_number)
            )
