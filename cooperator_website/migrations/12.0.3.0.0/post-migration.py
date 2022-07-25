from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    module_ids = env["ir.module.module"].search(
        [("name", "=", "cooperator_website_recaptcha"), ("state", "=", "uninstalled")]
    )
    if module_ids:
        module_ids.button_install()
