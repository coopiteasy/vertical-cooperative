from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    is_cooperator_template = fields.Boolean(string="Cooperator mail template")
