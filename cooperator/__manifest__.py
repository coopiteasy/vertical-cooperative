# Copyright 2013-2018 Open Architects Consulting SPRL.
# Copyright 2018      Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
#   Houssine BAKKALI - <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Cooperators",
    "summary": "Manage your cooperators",
    "version": "12.0.5.0.0",
    "depends": [
        "base",
        "web",
        "sale",
        "account",
        "base_iban",
        "product",
        "partner_contact_birthdate",
        "partner_firstname",
        "partner_contact_birthdate",
        "partner_contact_address",
        "partner_contact_gender",
        "email_template_config",
        "mail",
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "data": [
        "data/easy_my_coop_data.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizard/create_subscription_from_partner.xml",
        "wizard/update_partner_info.xml",
        "wizard/validate_subscription_request.xml",
        "wizard/update_share_line.xml",
        "views/subscription_request_view.xml",
        "views/mail_template_view.xml",
        "views/res_partner_view.xml",
        "views/subscription_register_view.xml",
        "views/operation_request_view.xml",
        "views/account_invoice_view.xml",
        "views/product_view.xml",
        "views/res_company_view.xml",
        "views/account_journal_view.xml",
        "views/menus.xml",
        "report/easy_my_coop_report.xml",
        "report/layout.xml",
        "report/cooperator_invoice_G002.xml",
        "report/cooperator_certificat_G001.xml",
        "report/cooperator_subscription_G001.xml",
        "report/cooperator_register_G001.xml",
        "data/mail_template_data.xml",  # Must be loaded after reports
    ],
    "demo": ["demo/coop.xml", "demo/users.xml"],
    "installable": True,
    "application": True,
}