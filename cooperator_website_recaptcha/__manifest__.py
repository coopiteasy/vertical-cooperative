# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cooperators Website Recaptcha",
    "summary": """
        Add Google Recaptcha to Subscription Request Form""",
    "version": "12.0.1.0.0",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "cooperator_website",
        "portal_recaptcha",
    ],
    "excludes": [],
    "data": [
        "views/res_company_views.xml",
        "views/subscription_template.xml",
    ],
    "demo": [],
    "qweb": [],
}
