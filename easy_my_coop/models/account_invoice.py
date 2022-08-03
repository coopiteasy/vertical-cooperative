from datetime import datetime

from odoo import api, fields, models


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    subscription_request = fields.Many2one('subscription.request',
                                           string='Subscription request')
    release_capital_request = fields.Boolean(
                                        string='Release of capital request')

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        values = super(account_invoice, self)._prepare_refund(
                                        invoice, date_invoice, date,
                                        description, journal_id)
        values['release_capital_request'] = self.release_capital_request

        return values

    def create_user(self, partner):
        user_obj = self.env['res.users']
        email = partner.email
        if partner.is_company:
            email = partner.company_email

        user = user_obj.search([('login', '=', email)])
        if not user:
            user = user_obj.search([('login', '=', email),
                                    ('active', '=', False)])
            if user:
                user.sudo().write({'active': True})
            else:
                user_values = {'partner_id': partner.id, 'login': email}
                user = user_obj.sudo()._signup_create_user(user_values)
                user.sudo().with_context({'create_user': True}).action_reset_password()

        return user

    def get_mail_template_certificate(self):
        if self.partner_id.member:
            return 'easy_my_coop.email_template_certificat_increase'
        return 'easy_my_coop.email_template_certificat'

    def get_sequence_register(self):
        return self.env.ref('easy_my_coop.sequence_subscription', False)

    def get_sequence_operation(self):
        return self.env.ref('easy_my_coop.sequence_register_operation', False)

    def get_share_line_vals(self, line, effective_date):
        return {
            'share_number': line.quantity,
            'share_product_id': line.product_id.id,
            'partner_id': self.partner_id.id,
            'share_unit_price': line.price_unit,
            'effective_date': effective_date
            }

    def get_subscription_register_vals(self, line, effective_date):
        return {
            'partner_id': self.partner_id.id,
            'quantity': line.quantity,
            'share_product_id': line.product_id.id,
            'share_unit_price': line.price_unit,
            'date': effective_date,
            'type': 'subscription'
            }

    def get_membership_vals(self):
        # flag the partner as an effective member
        # if not yet cooperator we generate a cooperator number
        if self.partner_id.member is False \
                and self.partner_id.old_member is False:
            sequence_id = self.get_sequence_register()
            sub_reg_num = sequence_id.next_by_id()
            vals = {'member': True, 'old_member': False,
                    'cooperator_register_number': int(sub_reg_num)
                    }
        elif self.partner_id.old_member:
            vals = {'member': True, 'old_member': False}

        return vals

    def set_membership(self):
        vals = self.get_membership_vals()
        self.partner_id.write(vals)

        return True

    def set_cooperator_effective(self, effective_date):
        sub_register_obj = self.env['subscription.register']
        share_line_obj = self.env['share.line']

        mail_template_id = self.get_mail_template_certificate()

        self.set_membership()

        sequence_operation = self.get_sequence_operation()
        sub_reg_operation = sequence_operation.next_by_id()

        certificate_email_template = self.env.ref(mail_template_id, False)

        for line in self.invoice_line_ids:
            sub_reg_vals = self.get_subscription_register_vals(line,
                                                               effective_date)
            sub_reg_vals['name'] = sub_reg_operation
            sub_reg_vals['register_number_operation'] = int(sub_reg_operation)

            sub_register_obj.create(sub_reg_vals)

            share_line_vals = self.get_share_line_vals(line, effective_date)
            share_line_obj.create(share_line_vals)

            if line.product_id.mail_template:
                certificate_email_template = line.product_id.mail_template

        # we send the email with the certificate in attachment
        certificate_email_template.sudo().send_mail(self.partner_id.id, False)

        if self.company_id.create_user:
            self.create_user(self.partner_id)

        return True

    def post_process_confirm_paid(self, effective_date):
        self.set_cooperator_effective(effective_date)

        return True

    def get_refund_domain(self, invoice):
        return [
                ('type', '=', 'out_refund'),
                ('origin', '=', invoice.move_name)
            ]

    @api.multi
    def action_invoice_paid(self):
        super(account_invoice, self).action_invoice_paid()
        for invoice in self:
            # we check if there is an open refund for this invoice. in this
            # case we don't run the process_subscription function as the
            # invoice has been reconciled with a refund and not a payment.
            domain = self.get_refund_domain(invoice)
            refund = self.search(domain)

            if invoice.partner_id.cooperator \
                    and invoice.release_capital_request \
                    and invoice.type == 'out_invoice' and not refund:
                # take the effective date from the payment.
                # by default the confirmation date is the payment date
                effective_date = datetime.now().strftime("%d/%m/%Y")

                if invoice.payment_move_line_ids:
                    move_line = invoice.payment_move_line_ids[0]
                    effective_date = move_line.date

                invoice.subscription_request.state = 'paid'
                invoice.post_process_confirm_paid(effective_date)
            # if there is a open refund we mark the subscription as cancelled
            elif invoice.partner_id.cooperator \
                    and invoice.release_capital_request \
                    and invoice.type == 'out_invoice' and refund:
                invoice.subscription_request.state = 'cancelled'
        return True
