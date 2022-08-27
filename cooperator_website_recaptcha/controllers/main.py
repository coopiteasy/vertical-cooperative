from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.cooperator_website.controllers.main import WebsiteSubscription


class RecaptchaWebsiteSubscription(WebsiteSubscription):
    def validation(  # noqa: C901 (method too complex)
        self, kwargs, logged, values, post_file
    ):
        result = super().validation(kwargs, logged, values, post_file)
        if result is not True:
            return result

        redirect = "cooperator_website.becomecooperator"

        is_company = kwargs.get("is_company") == "on"

        # TODO: Use a overloaded function with the captcha implementation
        if request.env["res.company"].captcha_type == "google":
            if (
                "g-recaptcha-response" not in kwargs
                or kwargs["g-recaptcha-response"] == ""
            ):
                values = self.fill_values(values, is_company, logged)
                values.update(kwargs)
                values["error_msg"] = _(
                    "the captcha has not been validated, please fill in the captcha"
                )

                return request.render(redirect, values)
            elif not request.env["portal.mixin"].is_captcha_valid(
                kwargs["g-recaptcha-response"]
            ):
                values = self.fill_values(values, is_company, logged)
                values.update(kwargs)
                values["error_msg"] = _(
                    "the captcha has not been validated, please fill in the captcha"
                )

                return request.render(redirect, values)

        return True
