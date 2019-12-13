# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Website Portal Extend',

    'summary': """
    Extension of Website Portal that show correctly information about
    companies
    """,
    'description': """
    """,

    'author': 'Rémy Taymans',
    'license': 'AGPL-3',
    'version': '9.0.1.0.0',
    'website': "https://github.com/houssine78/vertical-cooperative",

    'category': 'Website',

    'depends': [
        'website',
        'website_portal_v10',
    ],

    'data': [
        'views/portal_website_templates.xml',
    ]
}
