import logging

from openerp.openupgrade import openupgrade

logger = logging.getLogger("OpenUpgrade")

column_renames = {
    "job_sync_line": [
        ("adresse", "address"),
        ("ville", "city"),
        ("codepostal", "zip"),
        ("sync_date", "date"),
    ]
}

tables_renames = [
    ("job_sync_line", "subscription_request"),
    ("job_sync", None),
    ("external_db", None),
]


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return

    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, tables_renames)
