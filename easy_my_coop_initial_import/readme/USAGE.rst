
:warning: This module assumes there is no whole in the "imported_cooperator_register_number".

Configuration steps:

1. Configure the `property_cooperator_account` in Settings > Company.
2. Create the Share product and generate the ExternalId. You can export the share product to generate the external Id.
3. Add `Import Manager` group to the importation users.
4. Ensure that the sequence 'Subscription Register' has the newt number to 1.
5. Uncheck all the emails configuration before the import

Execution steps:

1. Import SR with the `imported_cooperator_register_number` and `share_type/external_id`.
2. Open the SR validator wizard and check the flag `Force validate all in draft` and validate to validate the SR and generate the partner and the capital release invoice.
3. Open the 'Pay capital release invoice of imported subscriptions' wizard and configure the journal to use. Then execute the wizard thar enqueue a job to mask as paid all the capital release invoices.
4. Check all the emails configuration after the execution.
