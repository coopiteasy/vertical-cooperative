# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Cooperators API Logs",
    "version": "12.0.1.0.0",
    "depends": [],
    "author": "Coop IT Easy SC",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
        Helpers to log calls in and out of cooperators_api.
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/api_log_views.xml",
    ],
    "installable": True,
    "application": False,
}
