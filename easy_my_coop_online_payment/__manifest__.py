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
    "name": "Easy My Coop Online Payment",
    "version": "1.0",
    "depends": ["easy_my_coop",
                "website_payment",
                "payment_paypal"],
    "author": "Houssine BAKKALI <houssine@coopiteasy.be>",
    "category": "Cooperative management",
    'website': "www.coopiteasy.be",
    "description": """
    This module allows the cooperator to pay the subscribed shares online
    during the subscription process
    """,
    'data': [
        "views/online_payment_template.xml",
        "views/subscription_request_view.xml",
    ],
    'installable': False,
    'application': False,
}
