12.0.6.0.0 (2022-09-27)
~~~~~~~~~~~~~~~~~~~~~~~

backport changes from migration to 14.0.

**Features**

- remove subscription request ``subscription`` state (use ``new`` instead)
  (was used when creating a subscription request from a partner).
- refactor subscription request ``.create()`` method to handle both people
  and companies.
- add several subscription request tests.
- make country and language fields mandatory on the web form.
- some code refactoring and cleanup.
- improve ``fr`` and ``fr_be`` translations.


**Bugfixes**

- improve email and report templates: correct some strings, clean up
  some whitespace, and fix references to first name for companies
  (instead of displaying "false").
- fix partner matching by email or company register number when creating
  a subscription request.
- fix subscription request name for companies: use company name (like
  previously) instead of representative name. the name is displayed in
  the title of the form, and can be used to search.
- fix name of reports and attachments.


12.0.5.3.0 (2022-09-05)
~~~~~~~~~~~~~~~~~~~~~~~

**Improved Documentation**

- Adding USAGE.rst to inform that localization modules are necessary. (`#346 <https://github.com/coopiteasy/vertical-cooperative/issues/346>`_)


12.0.5.0.0 (2022-06-23)
~~~~~~~~~~~~~~~~~~~~~~~

**Deprecations and Removals**

- When no cooperator account is defined on the company, this module previously
  defaulted to the account with code '416000'. This behaviour has been removed
  because the code is Belgian-only. The functionality has been moved to
  ``l10n_be_cooperator``. (`#314 <https://github.com/coopiteasy/vertical-cooperative/issues/314>`_)


12.0.3.3.2 (2022-06-20)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Fix name computation crash (`#330 <https://github.com/coopiteasy/vertical-cooperative/issues/330>`_)
