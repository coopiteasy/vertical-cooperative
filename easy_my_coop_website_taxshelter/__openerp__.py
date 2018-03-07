# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Easy My Coop Tax Shelter Website',

    'summary': """
    Give access to Tax Shelter Report in the website portal.
    """,
    'description': """
    """,

    'author': 'Rémy Taymans',
    'license': 'AGPL-3',
    'version': '9.0.1.0',
    'website': "https://github.com/houssine78/vertical-cooperative",

    'category': 'Website, Cooperative Management',

    'depends': [
        'website',
        'website_portal_v10',
        'easy_my_coop_taxshelter_report',
    ],

    'data': [
        'views/easy_my_coop_website_taxshelter_templates.xml',
    ]
}
