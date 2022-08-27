# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import datetime

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    subscription_request = fields.Many2one(
        "subscription.request", string="Subscription request"
    )
    release_capital_request = fields.Boolean(string="Release of capital request")

    def _get_starting_sequence(self):
        self.ensure_one()
        if not self.release_capital_request:
            return super()._get_starting_sequence()
        starting_sequence = "%s/%04d/000" % (self.journal_id.code, self.date.year)
        return starting_sequence

    def _reverse_move_vals(self, default_values, cancel=True):
        values = super()._reverse_move_vals(default_values, cancel)
        values["release_capital_request"] = self.release_capital_request

        return values

    def _recompute_payment_terms_lines(self):
        super()._recompute_payment_terms_lines()
        subscription_request = self.subscription_request
        if not subscription_request:
            return
        # ensure payment terms lines use the account for subscription requests.
        payment_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        account = subscription_request.get_accounting_account()
        for line in payment_terms_lines:
            if line.account_id != account:
                line.account_id = account

    def create_user(self, partner):
        user_obj = self.env["res.users"]
        email = partner.email

        user = user_obj.search([("login", "=", email)])
        if not user:
            user = user_obj.search([("login", "=", email), ("active", "=", False)])
            if user:
                user.sudo().write({"active": True})
            else:
                user_values = {"partner_id": partner.id, "login": email}
                user = user_obj.sudo()._signup_create_user(user_values)
                user.sudo().with_context({"create_user": True}).action_reset_password()

        return user

    def get_mail_template_certificate(self):
        if self.partner_id.member:
            mail_template = "cooperator.email_template_certificat_increase"
        else:
            mail_template = "cooperator.email_template_certificat"
        return self.env.ref(mail_template)

    def get_sequence_register(self):
        return self.env.ref("cooperator.sequence_subscription", False)

    def get_sequence_operation(self):
        return self.env.ref("cooperator.sequence_register_operation", False)

    def get_share_line_vals(self, line, effective_date):
        return {
            "share_number": line.quantity,
            "share_product_id": line.product_id.id,
            "partner_id": self.partner_id.id,
            "share_unit_price": line.price_unit,
            "effective_date": effective_date,
        }

    def get_subscription_register_vals(self, line, effective_date):
        return {
            "partner_id": self.partner_id.id,
            "quantity": line.quantity,
            "share_product_id": line.product_id.id,
            "share_unit_price": line.price_unit,
            "date": effective_date,
            "type": "subscription",
        }

    def get_membership_vals(self):
        # flag the partner as an effective member
        # if not yet cooperator we generate a cooperator number
        vals = {}
        if self.partner_id.member is False and self.partner_id.old_member is False:
            sequence_id = self.get_sequence_register()
            sub_reg_num = sequence_id.next_by_id()
            vals = {
                "member": True,
                "old_member": False,
                "cooperator_register_number": int(sub_reg_num),
            }
        elif self.partner_id.old_member:
            vals = {"member": True, "old_member": False}

        return vals

    def set_membership(self):
        vals = self.get_membership_vals()
        self.partner_id.write(vals)

        return True

    def _send_certificate_mail(self, certificate_email_template, sub_reg_line):
        if self.company_id.send_certificate_email:
            # we send the email with the certificate in attachment
            certificate_email_template.sudo().send_mail(self.partner_id.id, False)

    def set_cooperator_effective(self, effective_date):
        sub_register_obj = self.env["subscription.register"]
        share_line_obj = self.env["share.line"]

        certificate_email_template = self.get_mail_template_certificate()

        self.set_membership()

        sequence_operation = self.get_sequence_operation()
        sub_reg_operation = sequence_operation.next_by_id()

        for line in self.invoice_line_ids:
            sub_reg_vals = self.get_subscription_register_vals(line, effective_date)
            sub_reg_vals["name"] = sub_reg_operation
            sub_reg_vals["register_number_operation"] = int(sub_reg_operation)

            sub_reg_line = sub_register_obj.create(sub_reg_vals)

            share_line_vals = self.get_share_line_vals(line, effective_date)
            share_line_obj.create(share_line_vals)

            if line.product_id.mail_template:
                certificate_email_template = line.product_id.mail_template

        self._send_certificate_mail(certificate_email_template, sub_reg_line)

        if self.company_id.create_user:
            self.create_user(self.partner_id)

        return True

    def post_process_confirm_paid(self, effective_date):
        self.set_cooperator_effective(effective_date)

        return True

    def get_refund_domain(self, invoice):
        return [
            ("move_type", "=", "out_refund"),
            ("invoice_origin", "=", invoice.name),
        ]

    def action_invoice_paid(self):
        super().action_invoice_paid()
        for invoice in self:
            # we check if there is an open refund for this invoice. in this
            # case we don't run the process_subscription function as the
            # invoice has been reconciled with a refund and not a payment.
            domain = self.get_refund_domain(invoice)
            refund = self.search(domain)

            if (
                invoice.partner_id.cooperator
                and invoice.release_capital_request
                and invoice.move_type == "out_invoice"
                and not refund
            ):
                # take the effective date from the payment.
                # by default the confirmation date is the payment date
                effective_date = datetime.now()

                payments = [p for p in self._get_reconciled_payments()]
                if payments:
                    payments.sort(key=lambda p: p.date)
                    effective_date = payments[-1].date

                invoice.subscription_request.state = "paid"
                invoice.post_process_confirm_paid(effective_date)
            # if there is a open refund we mark the subscription as cancelled
            elif (
                invoice.partner_id.cooperator
                and invoice.release_capital_request
                and invoice.move_type == "out_invoice"
                and refund
            ):
                invoice.subscription_request.state = "cancelled"
        return True

    def _get_capital_release_mail_template(self):
        return self.env.ref("cooperator.email_template_release_capital", False)

    def send_capital_release_request_mail(self):
        if self.company_id.send_capital_release_email:
            email_template = self._get_capital_release_mail_template()
            # we send the email with the capital release request in attachment
            # TODO remove sudo() and give necessary access right
            email_template.sudo().send_mail(self.id, True)
