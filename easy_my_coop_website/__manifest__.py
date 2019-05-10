# Copyright 2013-2018 Open Architects Consulting SPRL.
# Copyright 2018-Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Website",
    "version": "12.0.1.0.0",
    "depends": [
        "easy_my_coop",
        "website",
        "website_form_recaptcha",
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "www.coopiteasy.be",
    "license": "AGPL-3",
    "description": """
    This module adds the cooperator subscription form allowing to subscribe for
     shares online.
    """,
    'data': [
        'security/easy_my_coop_security.xml',
        'security/ir.model.access.csv',
        'wizard/create_subscription_from_partner.xml',
        'wizard/update_partner_info.xml',
        'wizard/validate_subscription_request.xml',
        'wizard/update_share_line.xml',
        'view/subscription_request_view.xml',
        'view/email_template_view.xml',
        'view/res_partner_view.xml',
        'view/cooperator_register_view.xml',
        'view/operation_request_view.xml',
        'view/account_invoice_view.xml',
        # 'view/subscription_template.xml',
        'view/product_view.xml',
        'view/res_company_view.xml',
        'view/account_journal_view.xml',
        'data/easy_my_coop_data.xml',
        'report/easy_my_coop_report.xml',
        'report/cooperator_invoice_G002.xml',
        'report/cooperator_certificat_G001.xml',
        'report/cooperator_subscription_G001.xml',
        'report/cooperator_register_G001.xml',
        'data/mail_template_data.xml',
    ],
    'installable': True,
    'application': True,
}
