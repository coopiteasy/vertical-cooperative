def migrate(cr, version):
    cr.execute(
        """
        update ir_model_data
        set noupdate = False
        where name in (
        'action_cooperator_invoices',
        'action_report_cooperator_register',
        'action_cooperator_report_certificat',
        'action_report_cooperator_register'
        )
        """
    )
