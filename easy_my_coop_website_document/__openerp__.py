# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Easy My Coop Website Document',

    'summary': """
    Show documents in the website.
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
        'easy_my_coop_document',
    ],

    'data': [
        'views/easy_my_coop_website_document_templates.xml',
        'security/easy_my_coop_website_document_security.xml',
        'security/ir.model.access.csv',
    ]
}
