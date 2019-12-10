from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = "mail.template"

    easy_my_coop = fields.Boolean(string="Easy my coop mail template")
