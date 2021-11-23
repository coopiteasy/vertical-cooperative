def migrate(cr, version):
    cr.execute("UPDATE subscription_request SET firstname='-' WHERE firstname IS NULL;")
    cr.execute("UPDATE subscription_request SET lastname='-' WHERE lastname IS NULL;")
