from openupgradelib import openupgrade

renamed_view_xml_ids = (
    (
        "cooperator_website.captcha_template",
        "cooperator_website_recaptcha.captcha_template",
    ),
)


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        "delete from ir_ui_view where name ilike 'res.company.form.captcha%';"
    )
    env.cr.execute(
        "delete from ir_ui_view where key = 'beesdoo_easy_my_coop.becomecooperator';"
    )
    env.cr.execute("delete from ir_ui_view where name ilike 'become%cooperator';")
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)
