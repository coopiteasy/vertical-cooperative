# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop API",
    "version": "12.0.0.0.1",
    "depends": [
        "base_rest",
        "easy_my_coop",
        "easy_my_coop_api_logs",
        "auth_api_key",  # todo conf running_env = dev
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
        Open Easy My Coop to the world: RESTful API.
    """,
    "data": [
        "security/ir_rule.xml",
        "views/external_id_mixin_views.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
    "application": False,
}
