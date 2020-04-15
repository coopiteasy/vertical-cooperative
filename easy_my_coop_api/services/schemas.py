# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.fields import Date


def date_validator(field, value, error):
    try:
        Date.from_string(value)
    except ValueError as e:
        return error(
            field, _("{} does not match format '%Y-%m-%d'".format(value))
        )


S_SUBSCRIPTION_REQUEST_GET = {"_id": {"type": "integer"}}

S_SUBSCRIPTION_REQUEST_RETURN_GET = {
    "id": {"type": "integer", "required": True},
    "email": {"type": "string", "required": True, "empty": False},
    "name": {"type": "string", "required": True, "empty": False},
    "date": {"type": "string", "required": True, "empty": False},
    "state": {"type": "string", "required": True, "empty": False},
    "ordered_parts": {"type": "integer", "required": True},
    "share_product": {
        "type": "dict",
        "schema": {
            "id": {"type": "integer", "required": True},
            "name": {"type": "string", "required": True, "empty": False},
        },
    },
    "address": {
        "type": "dict",
        "schema": {
            "street": {"type": "string", "required": True, "empty": False},
            "zip_code": {"type": "string", "required": True, "empty": False},
            "city": {"type": "string", "required": True, "empty": False},
            "country": {"type": "string", "required": True, "empty": False},
        },
    },
    "lang": {"type": "string", "required": True, "empty": False},
}

S_SUBSCRIPTION_REQUEST_SEARCH = {
    "date_from": {"type": "string", "check_with": date_validator},
    "date_to": {"type": "string", "check_with": date_validator},
}

S_SUBSCRIPTION_REQUEST_RETURN_SEARCH = {
    "count": {"type": "integer", "required": True},
    "rows": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": S_SUBSCRIPTION_REQUEST_RETURN_GET,
        },
    },
}

S_SUBSCRIPTION_REQUEST_CREATE = {
    "name": {"type": "string", "required": True, "empty": False},
    "email": {"type": "string", "required": True, "empty": False},
    "ordered_parts": {"type": "integer", "required": True},
    "share_product": {"type": "integer", "required": True},
    "address": {
        "type": "dict",
        "schema": {
            "street": {"type": "string", "required": True, "empty": False},
            "zip_code": {"type": "string", "required": True, "empty": False},
            "city": {"type": "string", "required": True, "empty": False},
            "country": {"type": "string", "required": True, "empty": False},
        },
    },
    "lang": {"type": "string", "required": True, "empty": False},
}

S_SUBSCRIPTION_REQUEST_UPDATE = {
    "name": {"type": "string"},
    "email": {"type": "string"},
    "ordered_parts": {"type": "integer"},
    "state": {"type": "string"},
    "address": {
        "type": "dict",
        "schema": {
            "street": {"type": "string"},
            "zip_code": {"type": "string"},
            "city": {"type": "string"},
            "country": {"type": "string"},
        },
    },
    "lang": {"type": "string"},
    "share_product": {"type": "integer"},
}
