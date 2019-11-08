from odoo import models, fields

EMAIL_TEMPLATE_IDS = [
    "easy_my_coop.email_template_release_capital",
    "easy_my_coop.email_template_confirmation",
    "easy_my_coop.email_template_confirmation_company",
    "easy_my_coop.email_template_certificat",
    "easy_my_coop.email_template_certificat_increase",
    "easy_my_coop.email_template_share_transfer",
    "easy_my_coop.email_template_share_update"
    ]


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def init(self):
        for template_id in EMAIL_TEMPLATE_IDS:
            mail_template = self.env.ref(template_id)
            mail_template.easy_my_coop = True

    easy_my_coop = fields.Boolean(string="Easy my coop mail template")
