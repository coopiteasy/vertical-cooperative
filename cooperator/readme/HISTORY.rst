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
