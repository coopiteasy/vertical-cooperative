# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import api, fields, models


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
                user_id = user_obj.sudo()._signup_create_user(user_values)
                user = user_obj.browse(user_id)
                user.sudo().with_context({'create_user': True}).action_reset_password()

        return True

    def set_cooperator_effective(self, effective_date):
        # flag the partner as a effective member
        mail_template_id = 'easy_my_coop.email_template_certificat'

        # if not yet cooperator we generate a cooperator number
        if self.partner_id.member is False and self.partner_id.old_member is False:
            sequence_id = self.env.ref('easy_my_coop.sequence_subscription', False)
            sub_reg_num = sequence_id.next_by_id()
            self.partner_id.write({
                'member': True, 'old_member': False,
                'cooperator_register_number': int(sub_reg_num)})
        elif self.partner_id.old_member:
            self.partner_id.write({'member': True, 'old_member': False})
        else:
            mail_template_id = 'easy_my_coop.email_template_certificat_increase'
        sequence_operation = self.env.ref('easy_my_coop.sequence_register_operation', False)
        sub_reg_operation = sequence_operation.next_by_id()

        certificat_email_template = self.env.ref(mail_template_id, False)

        for line in self.invoice_line_ids:
            self.env['subscription.register'].create({
                'name': sub_reg_operation,
                'register_number_operation': int(sub_reg_operation),
                'partner_id': self.partner_id.id,
                'quantity': line.quantity,
                'share_product_id': line.product_id.id,
                'share_unit_price': line.price_unit,
                'date': effective_date,
                'type': 'subscription'})

            self.env['share.line'].create({
                'share_number': line.quantity,
                'share_product_id': line.product_id.id,
                'partner_id': self.partner_id.id,
                'share_unit_price': line.price_unit,
                'effective_date': effective_date
                })
            if line.product_id.mail_template:
                certificat_email_template = line.product_id.mail_template

        # we send the email with the certificat in attachment
        certificat_email_template.send_mail(self.partner_id.id, False)

        if self.company_id.create_user:
            self.create_user(self.partner_id)

        return True

    def post_process_confirm_paid(self, effective_date):
        self.set_cooperator_effective(effective_date)

        return True

    @api.multi
    def confirm_paid(self):
        for invoice in self:
            super(account_invoice, invoice).confirm_paid()
            # we check if there is an open refund for this invoice. in this
            # case we don't run the process_subscription function as the
            # invoice has been reconciled with a refund and not a payment.
            refund = self.search([('type', '=', 'out_refund'),
                                  ('origin', '=', invoice.move_name)])

            if invoice.partner_id.cooperator and invoice.release_capital_request \
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
            elif invoice.partner_id.cooperator and invoice.release_capital_request \
                    and invoice.type == 'out_invoice' and refund:
                invoice.subscription_request.state = 'cancelled'
        return True
