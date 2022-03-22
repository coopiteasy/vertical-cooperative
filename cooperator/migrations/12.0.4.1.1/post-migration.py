def migrate(cr, version):
    cr.execute(
        """
with cooperator_account_configurations as (
    select (string_to_array(res_id, ','))[2]::integer
        as company_id,
           (string_to_array(value_reference, ','))[2]::integer
               as account_id
    from ir_property
    where name = 'property_cooperator_account'
    order by company_id
)
update res_company
set property_cooperator_account = account_id
from cooperator_account_configurations
where res_company.id = company_id;

delete
from ir_property
where name = 'property_cooperator_account';
        """
    )
