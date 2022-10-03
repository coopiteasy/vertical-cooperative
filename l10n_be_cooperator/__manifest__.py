# Copyright 2013-2018 Open Architects Consulting SPRL.
# Copyright 2018 Coop IT Easy SC (<http://www.coopiteasy.be>)
# - Houssine Bakkali <houssine@coopiteasy.be>
# - Elouan Le Bars <elouan@coopiteasy.be>
# - Rémy Taymans <remy@coopiteasy.be>
# - Manuel Claeys Bouuaert <manuel@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).#
{
    "name": "Cooperators Belgium",
    "summary": "Cooperators Belgium Localization",
    "version": "14.0.1.2.0",
    "depends": [
        "cooperator",
        "cooperator_website",
        "l10n_be",
    ],
    "author": "Coop IT Easy SC",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "reports/tax_shelter_report.xml",
        "reports/tax_shelter_resold_report.xml",  # todo remove?
        "reports/tax_shelter_subscription_report.xml",
        "reports/tax_shelter_shares_report.xml",
        "views/tax_shelter_declaration_view.xml",
        "views/subscription_template.xml",
        "data/mail_template_data.xml",
        "data/scheduler_data.xml",
    ],
    "demo": [
        "demo/tax_shelter_demo.xml",
    ],
    "auto-install": True,
}
