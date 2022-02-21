# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import json

from odoo.fields import Date


def dict_to_dump(content):
    return json.dumps(content).encode("utf-8")


NOT_FOUND_ERROR = {"name": "Not Found", "code": 404}
FORBIDDEN_ERROR = {"name": "Forbidden", "code": 403}
SERVER_ERROR = {"name": "Server Error", "code": 500}
NO_RESULT = {"count": 0, "rows": []}

SR_SEARCH_RESULT = {
    "count": 1,
    "rows": [
        {
            "id": 1,
            "date": "2020-05-14",
            "email": "manuel@demo.net",
            "address": {
                "city": "Brussels",
                "street": "schaerbeekstraat",
                "zip_code": "1111",
                "country": "BE",
            },
            "lang": "en_US",
            "ordered_parts": 3,
            "is_company": False,
            "firstname": "Manuel",
            "lastname": "Dublues",
            "share_product": {"name": "Part B - Worker", "id": 2},
            "state": "draft",
            "data_policy_approved": "some data_policy_approved data",
            "internal_rules_approved": "some internal_rules_approved data",
            "financial_risk_approved": "some financial_risk_approved data",
            "generic_rules_approved": True,
            "birthdate": "1990-12-21",
            "gender": "male",
            "iban": "98765434567",
            "phone": None,
            "skip_control_ng": True,
            "capital_release_request_date": None,
        }
    ],
}

SR_GET_RESULT = {
    "id": 1,
    "is_company": False,
    "firstname": "Robin",
    "lastname": "Des Bois",
    "date": "2020-05-14",
    "email": "manuel@demo.net",
    "address": {
        "city": "Brussels",
        "street": "schaerbeekstraat",
        "zip_code": "1111",
        "country": "BE",
    },
    "lang": "en_US",
    "ordered_parts": 3,
    "share_product": {"name": "Part B - Worker", "id": 2},
    "state": "draft",
    "data_policy_approved": "some data_policy_approved data",
    "internal_rules_approved": "some internal_rules_approved data",
    "financial_risk_approved": "some financial_risk_approved data",
    "generic_rules_approved": True,
    "birthdate": "1990-12-21",
    "gender": "male",
    "iban": "98765434567",
    "phone": None,
    "skip_control_ng": True,
    "capital_release_request_date": None,
}

SR_VALIDATE_RESULT = {
    "id": 1,
    "is_company": False,
    "firstname": "Robin",
    "lastname": "Des Bois",
    "date": "2020-05-14",
    "email": "manuel@demo.net",
    "address": {
        "city": "Brussels",
        "street": "schaerbeekstraat",
        "zip_code": "1111",
        "country": "BE",
    },
    "lang": "en_US",
    "ordered_parts": 3,
    "share_product": {"name": "Part B - Worker", "id": 2},
    "capital_release_request": [9999],
    "state": "done",
    "data_policy_approved": True,
    "internal_rules_approved": True,
    "financial_risk_approved": True,
    "generic_rules_approved": True,
    "birthdate": "1990-12-21",
    "gender": "male",
    "iban": "98765434567",
    "phone": None,
    "skip_control_ng": True,
    "capital_release_request_date": None,
}

AP_CREATE_RESULT = {
    "id": 9876,
    "journal": {"id": 1, "name": "bank"},
    "invoice": {
        "id": 9999,
        "name": ["SUBJ/2020/001"],
    },
    "payment_date": Date.to_string(Date.today()),
    "amount": 75.0,
    "communication": "SUBJ/2020/001",
}
