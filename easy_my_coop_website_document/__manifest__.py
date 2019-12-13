# Copyright 2018-Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Easy My Coop Website Document',
    "version": "12.0.1.0.0",
    'depends': [
        'website',
        'easy_my_coop_document',
    ],
    'author': 'Coop IT Easy SCRLfs',
    'license': 'AGPL-3',
    'category': 'Cooperative Management',
    "website": "https://coopiteasy.be",
    'description': """
    Show documents in the website.
    """,
    'data': [
        'views/easy_my_coop_website_document_templates.xml',
        'security/easy_my_coop_website_document_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': False,
    'application': False,
}
