from openupgradelib import openupgrade

renamed_menu_xml_ids = (
    (
        "cooperator.menu_becomecooperator",
        "cooperator_website.menu_becomecooperator",
    ),
)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, renamed_menu_xml_ids)
