# Copyright 2017 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Easy My Coop Default Payment Term",
    "version": "12.0.1.0.0",
    "depends": ["easy_my_coop"],
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "category": "Invoice",
    "website": "https://coopiteasy.be",
    "summary": """
        Add a configurable default payment term that is used
        automatically when creating a capital release request.""",
    "data": [
        "views/res_company_view.xml",
    ],
    "installable": True,
}
