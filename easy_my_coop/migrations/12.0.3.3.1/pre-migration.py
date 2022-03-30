def migrate(cr, version):
    cr.execute(
        "update subscription_request "
        "set name = firstname || ' ' || lastname "
        "where name is null or name = '';"
    )
