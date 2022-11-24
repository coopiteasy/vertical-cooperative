
[![Pre-commit Status](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/coopiteasy/vertical-cooperative/branch/12.0/graph/badge.svg)](https://codecov.io/gh/coopiteasy/vertical-cooperative)

<!-- /!\ do not modify above this line -->

## ⚠️ Important Notice

**Please note that the main modules from this repository are being moved to the [`cooperative` repository of the OCA](https://github.com/OCA/cooperative).**

# Vertical Cooperative

This project aim to deal with modules related to cooperatives management.

You'll find modules that:

 - Allow people to sign up as a member of the cooperative from website
 - Manage member's shares, loans and dividends
 - Manage cooperative membership

Please don't hesitate to suggest one of your modules to this project.

The French and Catalan documentation can be found [here](https://doc.it4socialeconomy.org/books/application-easy-my-coop).
This is part of the [IT 4 Social Economy](https://it4socialeconomy.org) initiative.
Contact Coop IT Easy or Coopdevs for more information.


<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[cooperator_api](cooperator_api/) | 12.0.2.0.0 |  | Open Cooperators to the world: RESTful API.
[cooperator_api_logs](cooperator_api_logs/) | 12.0.1.0.0 |  | Helpers to log calls in and out of cooperators_api.
[cooperator_website_recaptcha](cooperator_website_recaptcha/) | 12.0.1.0.1 |  | Add Google Recaptcha to Subscription Request Form
[cooperator_website_uppercase_lastname](cooperator_website_uppercase_lastname/) | 12.0.1.0.0 |  | This module UPPERCASES the last names of submitted requests
[easy_my_coop_loan](easy_my_coop_loan/) | 12.0.2.0.1 |  | This module allows to manage the bonds and subordinated loans subscription life cycle.
[easy_my_coop_loan_account](easy_my_coop_loan_account/) | 12.0.1.0.0 |  | This module brings the accounting part of the loan issue. It has for purpose to generate all the accounting entries to the covered use cases.
[easy_my_coop_loan_account_be](easy_my_coop_loan_account_be/) | 12.0.1.0.0 |  | This module install belgian localisation demo data for EMC loan account. It also trigger installation for the dependency module
[easy_my_coop_loan_bba](easy_my_coop_loan_bba/) | 12.0.1.0.0 |  | This module implements the bba structured communication on the loan line.
[easy_my_coop_loan_website](easy_my_coop_loan_website/) | 12.0.1.1.0 |  | This module implements the subscription page for bonds and subordinated loans.
[l10n_be_cooperator_portal](l10n_be_cooperator_portal/) | 12.0.1.1.0 |  | Give access to Tax Shelter Report in the portal.
[l10n_ch_cooperator](l10n_ch_cooperator/) | 12.0.1.3.0 |  | Cooperators Switzerland localization
[l10n_es_cooperator](l10n_es_cooperator/) | 12.0.0.1.0 |  | Cooperator localization for Spain
[l10n_fr_cooperator](l10n_fr_cooperator/) | 12.0.1.2.0 |  | This is the French localization for the Cooperators module
[portal_recaptcha](portal_recaptcha/) | 12.0.1.0.2 |  | Add google recaptcha to forms.
[theme_light](theme_light/) | 12.0.1.0.0 |  | extract of the theme zen


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[easy_my_coop_connector](easy_my_coop_connector/) | 12.0.0.0.1 (unported) |  | Connect to Easy My Coop RESTful API.
[easy_my_coop_dividend](easy_my_coop_dividend/) | 12.0.0.0.1 (unported) |  | Manage the dividend computation for a fiscal year.
[easy_my_coop_export_xlsx](easy_my_coop_export_xlsx/) | 12.0.0.0.1 (unported) |  | Generate a xlsx file with information on current state of subscription request, cooperators and capital release request.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license. Consult each module's
`__manifest__.py` file, which contains a `license` key that explains its
license.
