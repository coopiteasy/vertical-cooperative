from odoo import models

EMAIL_TEMPLATE_IDS = [
    "easy_my_coop_loan.loan_subscription_confirmation",
    "easy_my_coop_loan.loan_issue_payment_request",
    ]


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def init(self):
        for template_id in EMAIL_TEMPLATE_IDS:
            mail_template = self.env.ref(template_id)
            mail_template.easy_my_coop = True
