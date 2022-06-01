from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    # fixme
    easy_my_coop = fields.Boolean(string="Easy my coop mail template")
