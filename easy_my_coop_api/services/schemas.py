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


# todo consistency: S_SR_GET, S_SR_RETURN_GET, S_SR_POST ...


S_SUBSCRIPTION_REQUEST_BASE = {
    "name": {"type": "string", "required": True, "empty": False},
    "email": {"type": "string", "required": True, "empty": False},
    "ordered_parts": {"type": "integer", "required": True},
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

S_SUBSCRIPTION_REQUEST_GET = {
    **S_SUBSCRIPTION_REQUEST_BASE,
    **{
        "id": {"type": "integer", "required": True},
        "date": {"type": "string", "required": True, "empty": False},
        "share_product": {
            "type": "dict",
            "schema": {
                "id": {"type": "integer", "required": True},
                "name": {"type": "string", "required": True, "empty": False},
            },
        },
    },
}

S_SUBSCRIPTION_REQUEST_CREATE = {
    **S_SUBSCRIPTION_REQUEST_BASE,
    **{"share_product": {"type": "integer", "required": True}},
}

S_SUBSCRIPTION_REQUEST_LIST = {
    "count": {"type": "integer", "required": True},
    "rows": {
        "type": "list",
        "schema": {"type": "dict", "schema": S_SUBSCRIPTION_REQUEST_GET},
    },
}
