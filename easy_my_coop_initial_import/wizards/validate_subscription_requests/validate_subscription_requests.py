import logging

from odoo import api, fields, models

from odoo.addons.queue_job.job import job

log = logging.getLogger(__name__)


class ValidateSubscriptionRequest(models.TransientModel):
    _inherit = "validate.subscription.request"

    force_validate_all_in_draft = fields.Boolean("Force validate all in draft")

    @api.multi
    def validate(self):
        if self.force_validate_all_in_draft:
            self.with_delay().enqueue_sr_validation()
        else:
            super(ValidateSubscriptionRequest, self).validate()
        return True

    @job
    def enqueue_sr_validation(self):
        log.info("Preparing data to validate subscription requests...")
        subscription_requests = self.env["subscription.request"].search(
            [("state", "=", "draft")], order="capital_release_request_date"
        )
        for sr in subscription_requests:
            log.info(
                "Validating subscription requests {}".format(
                    sr.imported_cooperator_register_number
                )
            )
            # Why are we forcing the commit?
            # We can commit the transaction here because this method is a
            # job, and we want to save the changes done.
            # Then, when we requeue this job, it
            # continues from the last capital release invoice without payments.
            sr.validate_subscription_request()
            self.env.cr.commit()
            log.info(
                "Validated subscription requests {}".format(
                    sr.imported_cooperator_register_number
                )
            )
