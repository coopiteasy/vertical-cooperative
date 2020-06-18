from openupgradelib import openupgrade

xmlid_renames = [
    (
        "easy_my_coop.group_energiris_user",
        "easy_my_coop.group_easy_my_coop_user",
    ),
    (
        "easy_my_coop.group_energiris_manager",
        "easy_my_coop.group_easy_my_coop_manager",
    ),
]


def copy_records_module_category_cooperator_management(env):
    openupgrade.logged_query(
        env.cr,
        """
            CREATE TABLE res_groups_users_rel_module_category_cooperator_management AS
            SELECT gid, uid
            FROM res_groups_users_rel
            WHERE gid = (
                SELECT id
                FROM res_groups
                WHERE name = 'User'
                AND category_id = (
                    SELECT id
                    FROM ir_module_category
                    WHERE name = 'EasyMy Coop'
                )
            )
            ORDER BY gid,uid;""",
    )


def delete_records_module_category_cooperator_management(env):
    """"Since XML-ID module_category_cooperator_management is now flagged as noupdate="1",
    we need to manually delete it as well as other records that are linked to it
    """
    openupgrade.logged_query(
        env.cr,
        """
            DELETE
            FROM res_groups_users_rel
            WHERE gid = (
                SELECT id
                FROM res_groups
                WHERE name = 'User'
                AND category_id = (
                    SELECT id
                    FROM ir_module_category
                    WHERE name = 'EasyMy Coop'
                )
            );""",
    )
    openupgrade.logged_query(
        env.cr,
        """
            DELETE
            FROM res_groups
            WHERE name = 'User'
            AND category_id = (
                SELECT id
                FROM ir_module_category
                WHERE name = 'EasyMy Coop'
            );""",
    )
    openupgrade.logged_query(
        env.cr,
        """
            DELETE
            FROM ir_module_category
            WHERE name = 'EasyMy Coop';""",
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlid_renames)
    copy_records_module_category_cooperator_management(env)
    delete_records_module_category_cooperator_management(env)
