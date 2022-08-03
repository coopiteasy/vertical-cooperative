# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.fields import Date


def date_validator(field, value, error):
    try:
        Date.from_string(value)
    except ValueError:
        return error(field, _("{} does not match format '%Y-%m-%d'".format(value)))


S_MANY_2_ONE = {
    "type": "dict",
    "schema": {
        "id": {"type": "integer", "required": True},
        "name": {"type": "string", "required": True, "empty": False},
    },
}

S_SUBSCRIPTION_REQUEST_GET = {"_id": {"type": "integer"}}

S_SUBSCRIPTION_REQUEST_RETURN_GET = {
    "id": {"type": "integer", "required": True},
    "email": {"type": "string", "required": True, "empty": False},
    "is_company": {"type": "boolean", "required": True},
    "firstname": {"type": "string", "required": True, "empty": False},
    "lastname": {"type": "string", "required": True, "empty": False},
    "date": {"type": "string", "required": True, "empty": False},
    "state": {"type": "string", "required": True, "empty": False},
    "ordered_parts": {"type": "integer", "required": True},
    "share_product": S_MANY_2_ONE,
    "phone": {"type": "string", "required": True, "empty": False, "nullable": True},
    "iban": {"type": "string", "required": True, "empty": False, "nullable": True},
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
    "capital_release_request": {
        "type": "list",
        "schema": {"type": "integer"},
        "required": True,
        "empty": True,
    },
    "gender": {"type": "string", "required": True, "empty": False, "nullable": True},
    "birthdate": {"type": "string", "check_with": date_validator, "nullable": True},
    "capital_release_request_date": {
        "type": "string",
        "check_with": date_validator,
        "nullable": True,
    },
    "generic_rules_approved": {"type": "boolean", "required": True},
    "skip_control_ng": {"type": "boolean", "required": True},
    "data_policy_approved": {"type": "boolean", "required": True},
    "internal_rules_approved": {"type": "boolean", "required": True},
    "financial_risk_approved": {"type": "boolean", "required": True},
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
    "firstname": {"type": "string", "required": True, "empty": False},
    "lastname": {"type": "string", "required": True, "empty": False},
    "is_company": {"type": "boolean", "required": True},
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
    "phone": {"type": "string", "nullable": True},
    "iban": {"type": "string", "nullable": True},
    "gender": {"type": "string", "nullable": True},
    "birthdate": {"type": "string", "check_with": date_validator, "nullable": True},
    "capital_release_request_date": {
        "type": "string",
        "check_with": date_validator,
        "nullable": True,
    },
    "data_policy_approved": {"type": "boolean", "required": True},
    "internal_rules_approved": {"type": "boolean", "required": True},
    "financial_risk_approved": {"type": "boolean", "required": True},
    "generic_rules_approved": {"type": "boolean", "required": True},
    "skip_control_ng": {"type": "boolean"},
}

S_SUBSCRIPTION_REQUEST_UPDATE = {
    "firstname": {"type": "string"},
    "lastname": {"type": "string"},
    "is_company": {"type": "boolean"},
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
    "phone": {"type": "string"},
    "iban": {"type": "string"},
    "gender": {"type": "string"},
    "birthdate": {"type": "string", "check_with": date_validator},
    "capital_release_request_date": {"type": "string", "check_with": date_validator},
    "lang": {"type": "string"},
    "share_product": {"type": "integer"},
    "generic_rules_approved": {"type": "boolean"},
    "data_policy_approved": {"type": "boolean"},
    "internal_rules_approved": {"type": "boolean"},
    "financial_risk_approved": {"type": "boolean"},
    "skip_control_ng": {"type": "boolean"},
}

S_INVOICE_GET = {"_id": {"type": "integer"}}

S_INVOICE_LINE_RETURN_GET = {
    "type": "list",
    "schema": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True},
            "account": S_MANY_2_ONE,
            "product": S_MANY_2_ONE,
            "quantity": {"type": "float", "required": True},
            "price_unit": {"type": "float", "required": True},
        },
    },
    "required": True,
    "empty": True,
}

S_INVOICE_RETURN_GET = {
    "id": {"type": "integer", "required": True},
    "number": {"type": "string", "required": True, "empty": False},
    "state": {"type": "string", "required": True, "empty": False},
    "type": {"type": "string", "required": True, "empty": False},
    "date": {"type": "string", "required": True, "empty": False},
    "date_due": {"type": "string", "required": True, "empty": False},
    "date_invoice": {"type": "string", "required": True, "empty": False},
    "partner": S_MANY_2_ONE,
    "journal": S_MANY_2_ONE,
    "account": S_MANY_2_ONE,
    "subscription_request": {
        "type": "dict",
        "schema": {"id": {"type": "integer"}, "name": {"type": "string"}},
    },
    "invoice_lines": S_INVOICE_LINE_RETURN_GET,
}

S_PAYMENT_RETURN_GET = {
    "id": {"type": "integer", "required": True},
    "journal": S_MANY_2_ONE,
    "invoice": S_MANY_2_ONE,
    "payment_date": {"type": "string", "check_with": date_validator},
    "amount": {"type": "float", "required": True},
    "communication": {"type": "string", "required": True},
}

S_PAYMENT_CREATE = {
    "journal": {"type": "integer", "required": True},
    "invoice": {"type": "integer", "required": True},
    "payment_date": {"type": "string", "check_with": date_validator},
    "amount": {"type": "float", "required": True},
    "communication": {"type": "string", "required": True},
    "payment_type": {"type": "string", "required": True},
    "payment_method": {"type": "string", "required": True},
}
