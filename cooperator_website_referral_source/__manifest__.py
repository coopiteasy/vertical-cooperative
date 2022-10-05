# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Cooperator Website Refferral",
    "summary": """
        Add a Selection field in the form to select
        how the respondent discovered the cooperative.
        """,
    "version": "12.0.1.0.0",
    "category": "Cooperative management",
    "website": "https://github.com/OCA/cooperative",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "depends": ["cooperator_website"],
    "excludes": [],
    "data": [
        "security/ir.model.access.csv",
        "views/referral_source_view.xml",
        "views/subscription_request_view.xml",
        "views/res_partner_view.xml",
        "views/subscription_template.xml",
    ],
    "demo": [],
    "qweb": [],
}
