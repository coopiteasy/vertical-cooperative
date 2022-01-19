from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_subscription_request_payment_term = fields.Many2one(
        "account.payment.term",
        company_dependent=True,
        string="Default Payment Term",
        help="Default payment term to use when"
        "creating capital release request invoices",
    )
