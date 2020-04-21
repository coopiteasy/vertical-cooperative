# vertical-cooperative
This repository gather odoo modules for cooperatives

# MAKE TRAVIS GREEN AGAIN

pre-commit still issues these messages. They need to be fixed.

```
************* Module easy_my_coop.models.partner
easy_my_coop/models/partner.py:56: [E8103(sql-injection), ResPartner._invoice_total] SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection
************* Module partner_age.models.partner
partner_age/models/partner.py:13: [E8103(sql-injection), ResPartner._search_age] SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection
************* Module easy_my_coop_taxshelter_report.models.tax_shelter_declaration
easy_my_coop_taxshelter_report/models/tax_shelter_declaration.py:325: [E8102(invalid-commit), TaxShelterCertificate.send_certificates] Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction
************* Module easy_my_coop.models.account_invoice
easy_my_coop/models/account_invoice.py:11: [C8104(class-camelcase), account_invoice] Use `CamelCase` "AccountInvoice" in class name "account_invoice". You can use oca-autopep8 of https://github.com/OCA/maintainer-tools to auto fix it.
************* Module easy_my_coop.models.operation_request
easy_my_coop/models/operation_request.py:12: [C8104(class-camelcase), operation_request] Use `CamelCase` "OperationRequest" in class name "operation_request". You can use oca-autopep8 of https://github.com/OCA/maintainer-tools to auto fix it.
************* Module easy_my_coop.models.coop
easy_my_coop/models/coop.py:287: [C8108(method-compute), SubscriptionRequest] Name of compute method should start with "_compute_"
************* Module website_recaptcha_reloaded.models.res_config
website_recaptcha_reloaded/models/res_config.py:7: [C8104(class-camelcase), website_config_settings] Use `CamelCase` "WebsiteConfigSettings" in class name "website_config_settings". You can use oca-autopep8 of https://github.com/OCA/maintainer-tools to auto fix it.
************* Module easy_my_coop.models.company
easy_my_coop/models/company.py:61: [C8108(method-compute), ResCompany] Name of compute method should start with "_compute_"

pylint with mandatory checks.............................................Failed
- hook id: pylint
- exit code: 18

************* Module easy_my_coop.models.partner
easy_my_coop/models/partner.py:56: [E8103(sql-injection), ResPartner._invoice_total] SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection
************* Module partner_age.models.partner
partner_age/models/partner.py:13: [E8103(sql-injection), ResPartner._search_age] SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection
************* Module easy_my_coop.models.account_invoice
easy_my_coop/models/account_invoice.py:11: [C8104(class-camelcase), account_invoice] Use `CamelCase` "AccountInvoice" in class name "account_invoice". You can use oca-autopep8 of https://github.com/OCA/maintainer-tools to auto fix it.
************* Module easy_my_coop.models.operation_request
easy_my_coop/models/operation_request.py:12: [C8104(class-camelcase), operation_request] Use `CamelCase` "OperationRequest" in class name "operation_request". You can use oca-autopep8 of https://github.com/OCA/maintainer-tools to auto fix it.
************* Module easy_my_coop.models.coop
easy_my_coop/models/coop.py:287: [C8108(method-compute), SubscriptionRequest] Name of compute method should start with "_compute_"
************* Module website_recaptcha_reloaded.models.res_config
website_recaptcha_reloaded/models/res_config.py:7: [C8104(class-camelcase), website_config_settings] Use `CamelCase` "WebsiteConfigSettings" in class name "website_config_settings". You can use oca-autopep8 of https://github.com/OCA/maintainer-tools to auto fix it.
************* Module easy_my_coop.models.company
easy_my_coop/models/company.py:61: [C8108(method-compute), ResCompany] Name of compute method should start with "_compute_"
```
