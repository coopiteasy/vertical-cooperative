from odoo import api, models, fields
from odoo.addons.queue_job.job import job


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
        subscription_requests = self.env["subscription.request"].search(
            [
                ("state", "=", "draft")
            ],
            order="capital_release_request_date"
        )
        for sr in subscription_requests:
            try:
                sr.validate_subscription_request()
                self.env.cr.commit()
            except Exception as error:
                self.env.cr.commit()
                raise error

