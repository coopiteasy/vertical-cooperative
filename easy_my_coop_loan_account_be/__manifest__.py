# Copyright 2020 - ongoing Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Loan Account Belgium",
    "version": "12.0.1.0.0",
    "depends": [
        "easy_my_coop",
        "easy_my_coop_be",
        "easy_my_coop_loan_bba",
        "easy_my_coop_loan_account",
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
    This module install belgian localisation demo data for EMC loan account.
    It also trigger installation for the dependency module
    """,
    "data": [],
    "demo": ["demo/emc_loan_account_demo.xml"],
    "installable": True,
}
