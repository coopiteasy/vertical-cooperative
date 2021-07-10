from openupgradelib import openupgrade


def update_records_module_category_cooperator_management(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE
            res_groups_users_rel_module_category_cooperator_management
            SET gid = (
                SELECT id
                FROM res_groups
                WHERE name = 'User'
                AND category_id = (
                    SELECT id
                    FROM ir_module_category
                    WHERE name = 'Cooperative Management'
                    )
                );""",
    )

    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO res_groups_users_rel (gid, uid)
            SELECT gid, uid FROM res_groups_users_rel_module_category_cooperator_management
            ON CONFLICT DO NOTHING;""",
    )


def drop_records_module_category_cooperator_management(env):
    openupgrade.logged_query(
        env.cr,
        """
            DROP TABLE res_groups_users_rel_module_category_cooperator_management;""",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_records_module_category_cooperator_management(env)
    drop_records_module_category_cooperator_management(env)
