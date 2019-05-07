# Copyright 2015-Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Theme light',
    'description': 'extract of the theme zen',
    'category': 'Website',
    'version': '1.0',
    'author': 'Benjamin Dugardin',
    'author': 'Houssine BAKKALI',
    'website': "www.coopiteasy.be",
    'depends': ['base',
                'web',
                'website_theme_install'
                ],
    'data': [
        'views/layout_template.xml',
        'report/header_report_G002.xml',
    ],
    'application': True,
}