# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cooperators Website Recaptcha",
    "summary": """
        TODO""",
    "version": "12.0.1.0.0",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "author": "Coop IT Easy SCRLfs",
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
