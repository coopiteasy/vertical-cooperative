# Copyright 2019      Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Loan Issues Website",
    "version": "12.0.1.0.1",
    "depends": [
        "easy_my_coop_loan",
        "easy_my_coop_website_portal",
        "auth_company_signup",
        "website",
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
    This module implements the subscription page
    for bonds and subordinated loans.
    """,
    "data": ["data/website_loan_data.xml", "template/loan_issue_template.xml"],
    "installable": True,
}
