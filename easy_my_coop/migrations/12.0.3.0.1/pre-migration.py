from openupgradelib import openupgrade

xmlid_renames = [
    ('easy_my_coop.group_energiris_user',
     'easy_my_coop.group_easy_my_coop_user'),
    ('easy_my_coop.group_energiris_manager',
     'easy_my_coop.group_easy_my_coop_manager'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlid_renames)
