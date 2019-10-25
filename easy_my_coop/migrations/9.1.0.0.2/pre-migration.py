# -*- coding: utf-8 -*-

def migrate(cr, version):
    if not version:
        return

    cr.execute("UPDATE res_company "
                "SET internal_rules_approval_required = FALSE "
                "WHERE display_internal_rules_approval = FALSE")
    cr.execute("UPDATE res_company "
                "SET data_policy_approval_required = FALSE "
                "WHERE display_data_policy_approval = FALSE")
    cr.execute("UPDATE res_company "
                "SET financial_risk_approval_required = FALSE "
                "WHERE display_financial_risk_approval = FALSE")
