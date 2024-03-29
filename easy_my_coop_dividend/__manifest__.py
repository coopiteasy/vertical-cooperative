#    Copyright (C) 2013-2018 Open Architects Consulting SPRL.
#    Copyright (C) 2013-2018 Coop IT Easy SC.
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
    "name": "Easy My Coop Dividend Engine",
    "summary": """
    Manage the dividend computation for a fiscal year.
    """,
    "author": "Houssine BAKKALI, <houssine@coopiteasy.be>",
    "license": "AGPL-3",
    "version": "12.0.0.0.1",
    "website": "https://coopiteasy.be",
    "category": "Cooperative Management",
    "depends": ["cooperator"],
    "data": ["security/ir.model.access.csv", "views/dividend_views.xml"],
    "installable": False,
}
