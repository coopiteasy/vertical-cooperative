from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        update ir_ui_view set active='f' where name ilike
        'res_config_settings_view_form_inherit_website'
        """
    )

    env.cr.execute(
        "select recaptcha_key_site, recaptcha_key_secret "
        "from website order by id limit 1"
    )
    recaptcha_key_site, recaptcha_key_secret = env.cr.fetchone()
    ir_config_parameter = env["ir.config_parameter"]
    ir_config_parameter.set_param(
        "portal_recaptcha.recaptcha_key_site", recaptcha_key_site
    )
    ir_config_parameter.set_param(
        "portal_recaptcha.recaptcha_key_secret", recaptcha_key_secret
    )
