# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2017 Open Architects Consulting SPRL.
#    Copyright (C) 2017-2018 Coop IT Easy SCRL.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Easy My Coop",
    "version": "1.0",
    "depends": ["base", 
                "sale", 
                "purchase",
                "account_accountant",
                "product",
                "partner_firstname",
                "partner_contact_birthdate",
                "website",
                "website_recaptcha_reloaded",
                "theme_light",
                "base_iban",
                "email_template_config",
                ],
    "author": "Houssine BAKKALI <houssine@coopiteasy.be>",
    "category": "Cooperative management",
    "description": """
    This module allows to manage the cooperator subscription and all the cooperative business processes.    
    """,
    'data': [
        'security/easy_my_coop_security.xml',
        'security/ir.model.access.csv',
        'wizard/create_subscription_from_partner.xml',
        'wizard/update_partner_info.xml',
        'view/subscription_request_view.xml',
        'view/email_template_view.xml',  
        'view/res_partner_view.xml',
        'view/cooperator_register_view.xml',
        'view/operation_request_view.xml',
        'view/account_invoice_view.xml',
        'view/subscription_template.xml',
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
        #'wizard/cooperative_history_wizard.xml',
    ],
    'installable': True,
    'application': True,
}