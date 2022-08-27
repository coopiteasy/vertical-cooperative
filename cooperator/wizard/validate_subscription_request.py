from odoo import models


# no need for a wizard here, a server action would do the trick
class ValidateSubscriptionRequest(models.TransientModel):
    _name = "validate.subscription.request"
    _description = "Validate subscription request"

    def validate(self):
        selected_requests = self.env["subscription.request"].browse(
            self._context.get("active_ids")
        )
        subscription_requests = selected_requests.filtered(
            lambda record: record.state in ["draft", "waiting"]
        )

        for subscription_request in subscription_requests:
            subscription_request.validate_subscription_request()
        return True
