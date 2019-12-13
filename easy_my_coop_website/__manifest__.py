# Copyright 2013-2018 Open Architects Consulting SPRL.
# Copyright 2018-Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Website",
    "version": "12.0.1.0.0",
    "depends": [
        "easy_my_coop",
        "website",
        "website_recaptcha_reloaded",
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "description": """
    This module adds the cooperator subscription form allowing to subscribe for
     shares online.
    """,
    'data': [
        'views/subscription_template.xml',
        'data/website_cooperator_data.xml',
    ],
    'installable': True,
    'application': True,
}
