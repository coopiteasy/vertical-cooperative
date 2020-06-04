# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Connector",
    "version": "12.0.0.0.1",
    "depends": ["easy_my_coop"],
    "author": "Coop IT Easy SCRLfs",
    "category": "Connector",
    "website": "www.coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
        Connect to Easy My Coop RESTful API.
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/emc_backend.xml",
        "views/emc_bindings.xml",
        "wizards/emc_history_import_sr.xml",
        "views/actions.xml",
        "views/menus.xml",
        "data/cron.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
    "application": False,
}
