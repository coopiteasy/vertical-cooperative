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
            "name": "Manuel Dublues",
            "share_product": {"name": "Part B - Worker", "id": 31},
            "state": "draft",
        }
    ],
}

SR_GET_RESULT = {
    "id": 1,
    "name": "Robin Des Bois",
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
    "share_product": {"name": "Part B - Worker", "id": 31},
    "state": "draft",
}

SR_VALIDATE_RESULT = {
    "id": 9999,
    "number": "SUBJ/2020/001",
    "date_due": "2020-08-12",
    "state": "open",
    "date_invoice": "2020-08-12",
    "date": "2020-08-12",
    "type": "out_invoice",
    "subscription_request": {"name": "Manuel Dublues", "id": 1},
    "partner": {"name": "Manuel Dublues", "id": 1},
    "invoice_lines": [
        {
            "price_unit": 25.0,
            "quantity": 3.0,
            "account": {"name": "Product Sales", "id": 2},
            "name": "Part B - Worker",
            "product": {"name": "Part B - Worker", "id": 2},
        }
    ],
    "journal": {"name": "Subscription Journal", "id": 1},
    "account": {"name": "Cooperators", "id": 1},
}

AP_CREATE_RESULT = {
    "id": 9876,
    "journal": {"id": 1, "name": "bank"},
    "invoice": {
        "id": SR_VALIDATE_RESULT["id"],
        "name": SR_VALIDATE_RESULT["number"],
    },
    "payment_date": Date.to_string(Date.today()),
    "amount": 75.0,
    "communication": SR_VALIDATE_RESULT["number"],
}
