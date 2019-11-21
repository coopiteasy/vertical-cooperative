from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = "mail.template"

#     def init(self):
#         for template_id in EMAIL_TEMPLATE_IDS:
#             mail_template = self.env.ref(template_id)
#             mail_template.easy_my_coop = True

    easy_my_coop = fields.Boolean(string="Easy my coop mail template")
