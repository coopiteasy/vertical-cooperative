# -*- coding: utf-8 -*-

#    Copyright (C) 2013-2018 Open Architects Consulting SPRL.
#    Copyright (C) 2013-2018 Coop IT Easy SCRLfs.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
##############################################################################


{
    'name': 'Easy My Coop Dividend Engine',

    'summary': """
    Manage the dividend calculation for a fiscal year.
    """,
    'description': """
    This module allows to calculate the dividend to give to a cooperator base
    on the amount of his shares, the percentage allocated and for how long the
    shares have been owned on prorata temporis calculation.
    """,

    'author': 'Houssine BAKKALI, <houssine@coopiteasy.be>',
    'license': 'AGPL-3',
    'version': '9.0.1.0',
    'website': "www.coopiteasy.be",

    'category': 'Cooperative Management',

    'depends': [
        'easy_my_coop',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/dividend_views.xml',
    ],
    'installable': False,
}
