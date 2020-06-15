# Copyright 2013-2018 Open Architects Consulting SPRL.
# Copyright 2018      Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine Bakkali <houssine@coopiteasy.be>
# - Elouan Le Bars <elouan@coopiteasy.be>
# - Rémy Taymans <remy@coopiteasy.be>
# - Manuel Claeys Bouuaert <manuel@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    # todo check ir model access
    "name": "Easy My Coop tax shelter report",
    "version": "12.0.1.0.1",
    "depends": ["easy_my_coop"],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
    This module allows you to create a fiscal declaration year and to print
    tax shelter declaration for each cooperator.
    """,
    "data": [
        "security/ir.model.access.csv",
        "reports/tax_shelter_report.xml",
        "reports/tax_shelter_resold_report.xml",  # todo remove?
        "reports/tax_shelter_subscription_report.xml",
        "reports/tax_shelter_shares_report.xml",
        "views/tax_shelter_declaration_view.xml",
        "data/mail_template_data.xml",
        "data/scheduler_data.xml",
    ],
    "demo": ["demo/tax_shelter_demo.xml"],
    "installable": True,
}
