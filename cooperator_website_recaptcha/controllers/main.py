from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.cooperator_website.controllers.main import WebsiteSubscription


class RecaptchaWebsiteSubscription(WebsiteSubscription):
    def _additional_validate(self, kwargs, logged, values, post_file):
        result = super()._additional_validate(kwargs, logged, values, post_file)
        if result is not True:
            return result
        result, error_msg = request.env["portal.mixin"].is_captcha_valid(kwargs)
        if not result:
            values["error_msg"] = _("Error validating the CAPTCHA: {0}").format(
                error_msg
            )
        return result
