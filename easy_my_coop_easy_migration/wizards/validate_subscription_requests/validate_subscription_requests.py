from odoo import api, models, fields
from odoo.addons.queue_job.job import job


class ValidateSubscriptionRequest(models.TransientModel):
    _inherit = "validate.subscription.request"

    force_validate_all_in_draft = fields.Boolean("Force validate all in draft")

    @api.multi
    def validate(self):
        if self.force_validate_all_in_draft:
            subscription_requests = self.env["subscription.request"].search([
                ("state", "=", "draft")
            ])
            for sr in subscription_requests:
                self.with_delay().enqueue_sr_validation(sr)
        return True

    @job
    def enqueue_sr_validation(self, sr):
        sr.validate_subscription_request()

