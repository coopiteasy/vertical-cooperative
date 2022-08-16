# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


MAIL_TEMPLATES = [
    "email_template_release_capital",
    "email_template_confirmation",
    "email_template_waiting_list",
    "email_template_confirmation_company",
    "email_template_certificat",
    "email_template_certificat_increase",
    "email_template_share_transfer",
    "email_template_share_update",
]


def fill_account_move_columns(env):
    openupgrade.logged_query(
        env.cr,
        """
        update account_move as am
        set subscription_request = ai.subscription_request,
        release_capital_request = ai.release_capital_request
        from account_invoice as ai
        where am.old_invoice_id = ai.id
        """,
    )


def reload_mail_templates(env):
    # force reload of mail templates, since they are marked as noupdate. it
    # would be possible to reload only what has changed, but there are too
    # many changes, so it is easier to reload everything. warning: any change
    # made to these will be lost.
    openupgrade.load_data(env.cr, "cooperator", "data/mail_template_data.xml")
    # delete the translations so that they can be updated (because the records
    # are marked as noupdate).
    openupgrade.delete_record_translations(env.cr, "cooperator", MAIL_TEMPLATES)


@openupgrade.migrate()
def migrate(env, version):
    fill_account_move_columns(env)
    reload_mail_templates(env)
