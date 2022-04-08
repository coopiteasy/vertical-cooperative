# Copyright 2022 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import http

from odoo.addons.easy_my_coop_website.controllers.main import WebsiteSubscription


class WebsiteSubscriptionUppercase(WebsiteSubscription):
    @http.route(
        ["/subscription/subscribe_share"],
        type="http",
        auth="public",
        website=True,
    )
    def share_subscription(self, **kwargs):
        if "lastname" in kwargs:
            kwargs["lastname"] = kwargs["lastname"].upper()
        return super().share_subscription(**kwargs)
