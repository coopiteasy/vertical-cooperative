#    Copyright (C) 2018- Coop IT Easy SC.
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
    "name": "Easy My Coop Export XLSX",
    "summary": """
    Generate a xlsx file with information on current state of subscription
    request, cooperators and capital release request.
    """,
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "version": "12.0.0.0.1",
    "website": "https://coopiteasy.be",
    "category": "Cooperative Management",
    "depends": ["cooperator"],
    "external_dependencies": {"python": ["xlsxwriter"]},
    "data": ["wizard/export_global_wizard.xml"],
    "installable": False,
}
