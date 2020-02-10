# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2017 Open Architects Consulting SPRL.
#    Copyright (C) 2018- Coop IT Easy SCRLfs.
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
    # todo check ir model access
    "name": "Easy My Coop tax shelter report",
    "version": "1.0",
    "depends": ["easy_my_coop"],
    "author": "Houssine BAKKALI <houssine@coopiteasy.be>",
    "category": "Cooperative management",
    'website': "www.coopiteasy.be",
    "license": "AGPL-3",
    "description": """
    This module allows to create a fiscal declaration year and to print
    tax shelter declaration each cooperator
    """,
    'data': [
        'security/ir.model.access.csv',
        'reports/tax_shelter_report.xml',
        'reports/tax_shelter_subscription_report.xml',
        'reports/tax_shelter_shares_report.xml',
        'views/tax_shelter_declaration_view.xml',
        'data/mail_template_data.xml',
        'data/scheduler_data.xml',
    ],
    'installable': True,
}
