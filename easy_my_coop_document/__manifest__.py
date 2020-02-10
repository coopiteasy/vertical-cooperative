# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    # migrate in v12 and isolate from emc
    # add manager group or use relevant existing group
    # add ir.model.access rules for that user
    'name': 'Easy My Coop Document',

    'summary': """
    Manage the documents of your cooperative.
    """,
    'description': """
    """,

    'author': 'Rémy Taymans',
    'license': 'AGPL-3',
    'version': '9.0.1.0',
    'website': "https://github.com/houssine78/vertical-cooperative",

    'category': 'Cooperative Management',

    'depends': [
        'base',
        'web',
        'mail',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/easy_my_coop_document_menu.xml',
        'views/easy_my_coop_document_views.xml',
    ]
}
