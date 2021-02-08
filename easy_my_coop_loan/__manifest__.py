# Copyright 2019      Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Bond and Subordinated Loan Issues",
    "version": "12.0.1.0.2",
    "depends": ["easy_my_coop"],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "http://www.coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
    This module allows to manage the bonds and
    subordinated loans subscription life cycle.
    """,
    "data": [
        "security/ir.model.access.csv",
        "data/actions.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        "views/loan_view.xml",
        "views/partner_view.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/coop.xml"],
    "installable": True,
}
