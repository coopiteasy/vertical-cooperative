from openupgradelib import openupgrade

_field_renames = [
    ("website", "website", "recaptcha_site_key", "recaptcha_key_site"),
    ("website", "website", "recaptcha_private_key", "recaptcha_key_secret"),
    ("res.config.settings", "res_config_settings", "recaptcha_site_key", "recaptcha_key_site"),
    ("res.config.settings", "res_config_settings", "recaptcha_private_key", "recaptcha_key_secret"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
