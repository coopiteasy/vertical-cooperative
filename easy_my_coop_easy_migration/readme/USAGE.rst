Configuration steps:

1. Configure the `property_cooperator_account` in Settings > Company.
2. Create the Share product and generate the ExternalId. You can export the share product to generate the external Id.
3. Add `Migration Manager` group to the migration user.
4. Modify the Subscription Journal sequence implementation to NoGap: Settings > Technical > Sequences > Account Default Subscription Journal

Execution steps:

1. Import SR with the `migrated_cooperator_register_number` and `share_type/external_id`.
2. Open the SR validator wizard and check the flag `Force validate all in draft` and validate.
