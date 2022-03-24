
[![Pre-commit Status](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/coopiteasy/vertical-cooperative/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/coopiteasy/vertical-cooperative/branch/12.0/graph/badge.svg)](https://codecov.io/gh/coopiteasy/vertical-cooperative)

<!-- /!\ do not modify above this line -->

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
[cooperator](cooperator/) | 12.0.4.1.1 |  | Manage your cooperators
[cooperator_api](cooperator_api/) | 12.0.1.0.1 |  | Open Cooperators to the world: RESTful API.
[cooperator_api_logs](cooperator_api_logs/) | 12.0.0.0.1 |  | Helpers to log calls in and out of cooperators_api.
[cooperator_portal](cooperator_portal/) | 12.0.2.0.2 |  | Show cooperator information in the website portal.
[easy_my_coop_connector](easy_my_coop_connector/) | 12.0.0.0.1 |  | Connect to Easy My Coop RESTful API.
[easy_my_coop_es](easy_my_coop_es/) | 12.0.0.0.16 |  | Easy My Coop localization for Spain
[easy_my_coop_es_website](easy_my_coop_es_website/) | 12.0.0.0.6 |  | Easy My Coop Website localization for Spain
[easy_my_coop_loan](easy_my_coop_loan/) | 12.0.2.0.1 |  | This module allows to manage the bonds and subordinated loans subscription life cycle.
[easy_my_coop_loan_account](easy_my_coop_loan_account/) | 12.0.1.0.0 |  | This module brings the accounting part of the loan issue. It has for purpose to generate all the accounting entries to the covered use cases.
[easy_my_coop_loan_account_be](easy_my_coop_loan_account_be/) | 12.0.1.0.0 |  | This module install belgian localisation demo data for EMC loan account. It also trigger installation for the dependency module
[easy_my_coop_loan_bba](easy_my_coop_loan_bba/) | 12.0.1.0.0 |  | This module implements the bba structured communication on the loan line.
[easy_my_coop_loan_website](easy_my_coop_loan_website/) | 12.0.1.0.1 |  | This module implements the subscription page for bonds and subordinated loans.
[easy_my_coop_website](easy_my_coop_website/) | 12.0.2.0.6 |  | This module adds the cooperator subscription form allowing to subscribe for shares online.
[easy_my_coop_website_taxshelter](easy_my_coop_website_taxshelter/) | 12.0.1.0.0 |  | Give access to Tax Shelter Report in the website portal.
[l10n_be_cooperator](l10n_be_cooperator/) | 12.0.1.2.0 |  | Cooperators Belgium Localization
[l10n_ch_cooperator](l10n_ch_cooperator/) | 12.0.1.0.2 |  | Cooperators Switzerland localization
[l10n_fr_cooperator](l10n_fr_cooperator/) | 12.0.1.0.2 |  | This is the french localization for the Cooperators module
[partner_age](partner_age/) | 12.0.2.0.0 |  | This module computes the age of the partner.
[theme_light](theme_light/) | 12.0.1.0.0 |  | extract of the theme zen
[website_recaptcha_reloaded](website_recaptcha_reloaded/) | 12.0.0.0.1 |  | Add google recaptcha to forms.


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[easy_my_coop_dividend](easy_my_coop_dividend/) | 12.0.0.0.1 (unported) |  | Manage the dividend computation for a fiscal year.
[easy_my_coop_export_xlsx](easy_my_coop_export_xlsx/) | 12.0.0.0.1 (unported) |  | Generate a xlsx file with information on current state of subscription request, cooperators and capital release request.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license. Consult each module's
`__manifest__.py` file, which contains a `license` key that explains its
license.
