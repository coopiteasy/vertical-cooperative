# Copyright 2019      Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Easy My Coop Loan Issues Management",
    "version": "12.0.2.0.1",
    "depends": ["easy_my_coop"],
    "author": "Coop IT Easy SCRLfs",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
    This module allows to manage the bonds and
    subordinated loans subscription life cycle.
    """,
    "data": [
        "security/ir.model.access.csv",
        "data/actions.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        "data/loan_data.xml",
        "views/loan_view.xml",
        "views/loan_line_view.xml",
        "views/loan_interest_lines_view.xml",
        "views/partner_view.xml",
        "reports/loan_issue_line_report.xml",
        "reports/withholding_tax_declaration_report.xml",
        "reports/loan_reimbursement_report.xml",
        "reports/loan_report.xml",
        "wizards/payment_report_wizard.xml",
        "views/assets.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/coop.xml"],
    "installable": True,
}
