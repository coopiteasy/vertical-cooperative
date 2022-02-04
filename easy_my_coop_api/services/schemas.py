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


S_STRING = {"type": "string"}
S_REQUIRED_STRING = {"type": "string", "required": True, "empty": False}
S_INTEGER = {"type": "integer"}
S_REQUIRED_INTEGER = {"type": "integer", "required": True}
S_BOOLEAN = {"type": "boolean"}
S_REQUIRED_BOOLEAN = {"type": "boolean", "required": True}
S_DATE = {"type": "string", "check_with": date_validator}
S_REQUIRED_DATE = {"type": "string", "check_with": date_validator, "nullable": True}
S_REQUIRED_FLOAT = {"type": "float", "required": True}

S_MANY_2_ONE = {
    "type": "dict",
    "schema": {
        "id": S_REQUIRED_INTEGER,
        "name": S_REQUIRED_STRING,
    },
}

S_ADDRESS = {
    "type": "dict",
    "schema": {
        "street": S_STRING,
        "zip_code": S_STRING,
        "city": S_STRING,
        "country": S_STRING,
    },
}
S_REQUIRED_ADDRESS = {
    "type": "dict",
    "schema": {
        "street": S_REQUIRED_STRING,
        "zip_code": S_REQUIRED_STRING,
        "city": S_REQUIRED_STRING,
        "country": S_REQUIRED_STRING,
    },
}

S_SUBSCRIPTION_REQUEST_GET = {"_id": S_INTEGER}

S_SUBSCRIPTION_REQUEST_RETURN_GET = {
    "id": S_REQUIRED_INTEGER,
    "email": S_REQUIRED_STRING,
    "is_company": S_REQUIRED_BOOLEAN,
    "firstname": S_REQUIRED_STRING,
    "lastname": S_REQUIRED_STRING,
    "date": S_REQUIRED_STRING,
    "state": S_REQUIRED_STRING,
    "ordered_parts": S_REQUIRED_INTEGER,
    "share_product": S_MANY_2_ONE,
    "phone": {
        "type": "string",
        "required": True,
        "empty": False,
        "nullable": True,
    },
    "iban": {
        "type": "string",
        "required": True,
        "empty": False,
        "nullable": True,
    },
    "address": S_REQUIRED_ADDRESS,
    "lang": S_REQUIRED_STRING,
    "capital_release_request": {
        "type": "list",
        "schema": S_INTEGER,
        "required": True,
        "empty": True,
    },
    "gender": {"type": "string", "required": True, "empty": False, "nullable": True},
    "birthdate": S_REQUIRED_DATE,
    "capital_release_request_date": S_REQUIRED_DATE,
    "generic_rules_approved": S_REQUIRED_BOOLEAN,
    "skip_control_ng": S_REQUIRED_BOOLEAN,
    "data_policy_approved": S_REQUIRED_BOOLEAN,
    "internal_rules_approved": S_REQUIRED_BOOLEAN,
    "financial_risk_approved": S_REQUIRED_BOOLEAN,
}

S_SUBSCRIPTION_REQUEST_SEARCH = {
    "date_from": S_DATE,
    "date_to": S_DATE,
}

S_SUBSCRIPTION_REQUEST_RETURN_SEARCH = {
    "count": S_REQUIRED_INTEGER,
    "rows": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": S_SUBSCRIPTION_REQUEST_RETURN_GET,
        },
    },
}

S_SUBSCRIPTION_REQUEST_CREATE = {
    "firstname": S_REQUIRED_STRING,
    "lastname": S_REQUIRED_STRING,
    "is_company": S_REQUIRED_BOOLEAN,
    "email": S_REQUIRED_STRING,
    "ordered_parts": S_REQUIRED_INTEGER,
    "share_product": S_REQUIRED_INTEGER,
    "address": S_REQUIRED_ADDRESS,
    "lang": S_REQUIRED_STRING,
    "phone": {"type": "string", "nullable": True},
    "iban": {"type": "string", "nullable": True},
    "gender": {"type": "string", "nullable": True},
    "birthdate": S_REQUIRED_DATE,
    "capital_release_request_date": S_REQUIRED_DATE,
    "data_policy_approved": S_REQUIRED_BOOLEAN,
    "internal_rules_approved": S_REQUIRED_BOOLEAN,
    "financial_risk_approved": S_REQUIRED_BOOLEAN,
    "generic_rules_approved": S_REQUIRED_BOOLEAN,
    "skip_control_ng": S_BOOLEAN,
}

S_SUBSCRIPTION_REQUEST_UPDATE = {
    "firstname": S_STRING,
    "lastname": S_STRING,
    "is_company": S_BOOLEAN,
    "email": S_STRING,
    "ordered_parts": S_INTEGER,
    "state": S_STRING,
    "address": S_ADDRESS,
    "phone": S_STRING,
    "iban": S_STRING,
    "gender": S_STRING,
    "birthdate": S_DATE,
    "capital_release_request_date": S_DATE,
    "lang": S_STRING,
    "share_product": S_INTEGER,
    "generic_rules_approved": S_BOOLEAN,
    "data_policy_approved": S_BOOLEAN,
    "internal_rules_approved": S_BOOLEAN,
    "financial_risk_approved": S_BOOLEAN,
    "skip_control_ng": S_BOOLEAN,
}

S_INVOICE_GET = {"_id": S_INTEGER}

S_INVOICE_LINE_RETURN_GET = {
    "type": "list",
    "schema": {
        "type": "dict",
        "schema": {
            "name": S_REQUIRED_STRING,
            "account": S_MANY_2_ONE,
            "product": S_MANY_2_ONE,
            "quantity": S_REQUIRED_FLOAT,
            "price_unit": S_REQUIRED_FLOAT,
        },
    },
    "required": True,
    "empty": True,
}

S_INVOICE_RETURN_GET = {
    "id": S_REQUIRED_INTEGER,
    "number": S_REQUIRED_STRING,
    "state": S_REQUIRED_STRING,
    "type": S_REQUIRED_STRING,
    "date": S_REQUIRED_STRING,
    "date_due": S_REQUIRED_STRING,
    "date_invoice": S_REQUIRED_STRING,
    "partner": S_MANY_2_ONE,
    "journal": S_MANY_2_ONE,
    "account": S_MANY_2_ONE,
    "subscription_request": {
        "type": "dict",
        "schema": {
            "id": S_INTEGER,
            "name": S_STRING,
        },
    },
    "invoice_lines": S_INVOICE_LINE_RETURN_GET,
}

S_PAYMENT_RETURN_GET = {
    "id": S_REQUIRED_INTEGER,
    "journal": S_MANY_2_ONE,
    "invoice": S_MANY_2_ONE,
    "payment_date": S_DATE,
    "amount": S_REQUIRED_FLOAT,
    "communication": {"type": "string", "required": True},
}

S_PAYMENT_CREATE = {
    "journal": S_REQUIRED_INTEGER,
    "invoice": S_REQUIRED_INTEGER,
    "payment_date": S_DATE,
    "amount": S_REQUIRED_FLOAT,
    "communication": {"type": "string", "required": True},
    "payment_type": S_REQUIRED_STRING,
    "payment_method": S_REQUIRED_STRING,
}

S_PARTNER_GET = {"_id": S_INTEGER}

S_PARTNER_RETURN_GET = {
    "id": S_REQUIRED_INTEGER,
    "firstname": S_REQUIRED_STRING,
    "lastname": S_REQUIRED_STRING,
    "is_company": S_REQUIRED_BOOLEAN,
    "email": S_REQUIRED_STRING,
    "address": S_REQUIRED_ADDRESS,
    "birthdate": S_REQUIRED_DATE,
    "gender": {"type": "string", "required": True, "empty": False, "nullable": True},
    "lang": S_REQUIRED_STRING,
    "phone": S_REQUIRED_STRING,
    "company": S_MANY_2_ONE,
    "data_policy_approved": S_REQUIRED_BOOLEAN,
    "financial_risk_approved": S_REQUIRED_BOOLEAN,
    "generic_rules_approved": S_REQUIRED_BOOLEAN,
    "internal_rules_approved": S_REQUIRED_BOOLEAN,
}
