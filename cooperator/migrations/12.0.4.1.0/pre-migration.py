def migrate(cr, version):
    # (poorly named) view and data blocks the merge into cooperator
    cr.execute(
        """
delete from ir_model_data
where name = 'view_company_easy_my_coop_loan';
delete from ir_ui_view
where arch_fs = 'easy_my_coop_payment_term/views/res_company_view.xml';
        """
    )
    # save previous configuration
    cr.execute(
        """
alter table res_company
add column if not exists
    default_capital_release_request_payment_term
    integer
;

with cooperator_account_configurations as (
    select (string_to_array(res_id, ','))[2]::integer
               as company_id,
           (string_to_array(value_reference, ','))[2]::integer
               as payment_term_id
    from ir_property
    where name = 'default_subscription_request_payment_term'
    order by company_id
)
update res_company
set default_capital_release_request_payment_term = payment_term_id
from cooperator_account_configurations
where res_company.id = company_id;

delete
from ir_property
where name = 'default_subscription_request_payment_term';
"""
    )
