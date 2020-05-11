# Copyright 2018-Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Easy My Coop Tax Shelter Website",
    "version": "12.0.1.0.0",
    "depends": [
        "website",
        "website_portal_v10",
        "easy_my_coop_taxshelter_report",
        "report",
    ],
    "summary": "Give access to Tax Shelter Report in the website portal.",
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "category": "Cooperative Management",
    "website": "www.coopiteasy.be",
    "data": ["views/easy_my_coop_website_taxshelter_templates.xml"],
    "installable": False,
    "application": False,
}
