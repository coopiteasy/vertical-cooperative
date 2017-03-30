# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2016 Open Architects Consulting SPRL.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Easy My Coop Fr",
    "version": "1.0",
    "depends": ["easy_my_coop",
                "l10n_fr",
                "theme_light",],
    "author": "Houssine BAKKALI <houssine.bakkali@gmail.com>",
    "category": "Cooperative management",
    "description": """
    This is the french localization for the easy my coop module    
    """,
    'data': [
        'views/subscription_template.xml',
        'views/layout_template.xml',
        'views/certificate_template.xml'
    ],
    'installable': True,
}