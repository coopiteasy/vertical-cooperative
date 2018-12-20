# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class ValidateSubscriptionRequest(models.TransientModel):
    _name = "validate.subscription.request"
    _description = "Update Partner Info"

    @api.multi
    def validate(self):

        subscription_requests = self.filtered(lambda record: record.state in ['draft', 'waiting'])
        for subscription_request in subscription_requests:
            subscription_request.validate_subscription_request
        return True
