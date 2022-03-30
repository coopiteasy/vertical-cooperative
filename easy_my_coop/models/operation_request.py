# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OperationRequest(models.Model):
    _name = "operation.request"
    _description = "Operation request"

    def get_date_now(self):
        # fixme odoo 12 uses date types
        return datetime.strftime(datetime.now(), "%Y-%m-%d")

    @api.multi
    @api.depends("share_product_id", "share_product_id.list_price", "quantity")
    def _compute_subscription_amount(self):
        for operation_request in self:
            operation_request.subscription_amount = (
                operation_request.share_product_id.list_price
                * operation_request.quantity
            )

    request_date = fields.Date(
        string="Request date", default=lambda self: self.get_date_now()
    )
    effective_date = fields.Date(string="Effective date")
    partner_id = fields.Many2one(
        "res.partner",
        string="Cooperator",
        domain=[("member", "=", True)],
        required=True,
    )
    partner_id_to = fields.Many2one(
        "res.partner",
        string="Transfered to",
        domain=[("cooperator", "=", True)],
    )
    operation_type = fields.Selection(
        [
            ("subscription", "Subscription"),
            ("transfer", "Transfer"),
            ("sell_back", "Sell Back"),
            ("convert", "Conversion"),
        ],
        string="Operation Type",
        required=True,
    )
    share_product_id = fields.Many2one(
        "product.product",
        string="Share type",
        domain=[("is_share", "=", True)],
        required=True,
    )
    share_to_product_id = fields.Many2one(
        "product.product",
        string="Convert to this share type",
        domain=[("is_share", "=", True)],
    )
    share_short_name = fields.Char(
        related="share_product_id.short_name", string="Share type name"
    )
    share_to_short_name = fields.Char(
        related="share_to_product_id.short_name", string="Share to type name"
    )
    share_unit_price = fields.Float(
        related="share_product_id.list_price", string="Share price"
    )
    share_to_unit_price = fields.Float(
        related="share_to_product_id.list_price", string="Share to price"
    )
    subscription_amount = fields.Float(
        compute="_compute_subscription_amount", string="Operation amount"
    )
    quantity = fields.Integer(string="Number of share", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting", "Waiting"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("refused", "Refused"),
        ],
        string="State",
        required=True,
        default="draft",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        readonly=True,
        default=lambda self: self.env.user,
    )
    subscription_request = fields.One2many(
        "subscription.request",
        "operation_request_id",
        string="Share Receiver Info",
        help="In case on a transfer of"
        " share. If the share receiver"
        " isn't a effective member then a"
        " subscription form should"
        " be filled.",
    )
    receiver_not_member = fields.Boolean(string="Receiver is not a member")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )

    invoice = fields.Many2one("account.invoice", string="Invoice")

    @api.multi
    @api.constrains("effective_date")
    def _constrain_effective_date(self):
        for obj in self:
            if obj.effective_date and obj.effective_date > fields.Date.today():
                raise ValidationError(_("The effective date can not be in the future."))

    @api.multi
    def approve_operation(self):
        for rec in self:
            rec.write({"state": "approved"})

    @api.multi
    def refuse_operation(self):
        for rec in self:
            rec.write({"state": "refused"})

    @api.multi
    def submit_operation(self):
        for rec in self:
            rec.validate()
            rec.write({"state": "waiting"})

    @api.multi
    def cancel_operation(self):
        for rec in self:
            rec.write({"state": "cancelled"})

    @api.multi
    def reset_to_draft(self):
        for rec in self:
            rec.write({"state": "draft"})

    def get_total_share_dic(self, partner):
        total_share_dic = {}
        share_products = self.env["product.product"].search([("is_share", "=", True)])

        for share_product in share_products:
            total_share_dic[share_product.id] = 0

        for line in partner.share_ids:
            total_share_dic[line.share_product_id.id] += line.share_number

        return total_share_dic

    # This function doesn't handle the case of a cooperator can own
    # different kinds of share type
    def hand_share_over(self, partner, share_product_id, quantity):
        if not partner.member:
            raise ValidationError(
                _(
                    "This operation can't be executed if the"
                    " cooperator is not an effective member"
                )
            )

        share_ind = len(partner.share_ids)
        i = 1
        while quantity > 0:
            line = self.partner_id.share_ids[share_ind - i]
            if line.share_product_id.id == share_product_id.id:
                if quantity > line.share_number:
                    quantity -= line.share_number
                    line.unlink()
                else:
                    share_left = line.share_number - quantity
                    quantity = 0
                    line.write({"share_number": share_left})
            i += 1
        # if the cooperator sold all his shares he's no more
        # an effective member
        remaning_share_dict = 0
        for share_quant in self.get_total_share_dic(partner).values():
            remaning_share_dict += share_quant
        if remaning_share_dict == 0:
            self.partner_id.write({"member": False, "old_member": True})

    def has_share_type(self):
        for line in self.partner_id.share_ids:
            if line.share_product_id.id == self.share_product_id.id:
                return True
        return False

    def validate(self):
        if not self.has_share_type() and self.operation_type in [
            "sell_back",
            "transfer",
        ]:
            raise ValidationError(
                _(
                    "The cooperator doesn't own this share"
                    " type. Please choose the appropriate"
                    " share type."
                )
            )

        if self.operation_type in ["sell_back", "convert", "transfer"]:
            total_share_dic = self.get_total_share_dic(self.partner_id)

            if self.quantity > total_share_dic[self.share_product_id.id]:
                raise ValidationError(
                    _("The cooperator can't hand over more" " shares that he/she owns.")
                )

        if self.operation_type == "convert":
            if self.company_id.unmix_share_type:
                if self.share_product_id.code == self.share_to_product_id.code:
                    raise ValidationError(
                        _("You can't convert the share to" " the same share type.")
                    )
                if self.subscription_amount != self.partner_id.total_value:
                    raise ValidationError(
                        _("You must convert all the shares" " to the selected type.")
                    )
            else:
                if self.subscription_amount != self.partner_id.total_value:
                    raise ValidationError(
                        _(
                            "Converting just part of the"
                            " shares is not yet implemented"
                        )
                    )
        elif self.operation_type == "transfer":
            if (
                not self.receiver_not_member
                and self.company_id.unmix_share_type
                and (
                    self.partner_id_to.cooperator_type
                    and self.partner_id.cooperator_type
                    != self.partner_id_to.cooperator_type
                )
            ):
                raise ValidationError(
                    _(
                        "This share type could not be"
                        " transfered to " + self.partner_id_to.name
                    )
                )
            if self.partner_id_to.is_company and not self.share_product_id.by_company:
                raise ValidationError(
                    _("This share can not be" " subscribed by a company")
                )
            if (
                not self.partner_id_to.is_company
                and not self.share_product_id.by_individual
            ):
                raise ValidationError(
                    _("This share can not be" " subscribed an individual")
                )
            if (
                self.receiver_not_member
                and self.subscription_request
                and not self.subscription_request.validated
            ):
                raise ValidationError(
                    _(
                        "The information of the receiver"
                        " are not correct. Please correct"
                        " the information before"
                        " submitting"
                    )
                )

    def _get_share_transfer_mail_template(self):
        return self.env.ref("easy_my_coop.email_template_share_transfer", False)

    def _get_share_update_mail_template(self):
        return self.env.ref("easy_my_coop.email_template_share_update", False)

    def _send_share_transfer_mail(
        self, sub_register_line
    ):  # fixme unused argument is used in synergie project. Do not remove.
        if self.company_id.send_share_transfer_email:
            cert_email_template = self._get_share_transfer_mail_template()
            cert_email_template.send_mail(self.partner_id_to.id, False)

    def _send_share_update_mail(
        self, sub_register_line
    ):  # fixme unused argument is used in synergie project. Do not remove.
        if self.company_id.send_share_update_email:
            cert_email_template = self._get_share_update_mail_template()
            cert_email_template.send_mail(self.partner_id.id, False)

    def get_subscription_register_vals(self, effective_date):
        return {
            "partner_id": self.partner_id.id,
            "quantity": self.quantity,
            "share_product_id": self.share_product_id.id,
            "type": self.operation_type,
            "share_unit_price": self.share_unit_price,
            "date": effective_date,
        }

    @api.multi
    def execute_operation(self):
        self.ensure_one()

        if self.effective_date:
            effective_date = self.effective_date
        else:
            effective_date = self.get_date_now()
            self.effective_date = effective_date
        sub_request = self.env["subscription.request"]

        self.validate()

        if self.state != "approved":
            raise ValidationError(
                _("This operation must be approved" " before to be executed")
            )

        values = self.get_subscription_register_vals(effective_date)

        if self.operation_type == "sell_back":
            self.hand_share_over(self.partner_id, self.share_product_id, self.quantity)
        elif self.operation_type == "convert":
            amount_to_convert = self.share_unit_price * self.quantity
            convert_quant = int(amount_to_convert / self.share_to_product_id.list_price)
            remainder = amount_to_convert % self.share_to_product_id.list_price

            if convert_quant > 0 and remainder == 0:
                share_ids = self.partner_id.share_ids
                line = share_ids[0]
                if len(share_ids) > 1:
                    share_ids[1 : len(share_ids)].unlink()
                line.write(
                    {
                        "share_number": convert_quant,
                        "share_product_id": self.share_to_product_id.id,
                        "share_unit_price": self.share_to_unit_price,
                        "share_short_name": self.share_to_short_name,
                    }
                )
                values["share_to_product_id"] = self.share_to_product_id.id
                values["quantity_to"] = convert_quant
            else:
                raise ValidationError(
                    _("Converting just part of the" " shares is not yet implemented")
                )
        elif self.operation_type == "transfer":
            sequence_id = self.env.ref("easy_my_coop.sequence_subscription", False)
            partner_vals = {"member": True}
            if self.receiver_not_member:
                partner = self.subscription_request.create_coop_partner()
                # get cooperator number
                sub_reg_num = int(sequence_id.next_by_id())
                partner_vals.update(
                    sub_request.get_eater_vals(partner, self.share_product_id)
                )
                partner_vals["cooperator_register_number"] = sub_reg_num
                partner.write(partner_vals)
                self.partner_id_to = partner
            else:
                # means an old member or cooperator candidate
                if not self.partner_id_to.member:
                    if self.partner_id_to.cooperator_register_number == 0:
                        sub_reg_num = int(sequence_id.next_by_id())
                        partner_vals["cooperator_register_number"] = sub_reg_num
                    partner_vals.update(
                        sub_request.get_eater_vals(
                            self.partner_id_to, self.share_product_id
                        )
                    )
                    partner_vals["old_member"] = False
                    self.partner_id_to.write(partner_vals)
            # remove the parts to the giver
            self.hand_share_over(self.partner_id, self.share_product_id, self.quantity)
            # give the share to the receiver
            self.env["share.line"].create(
                {
                    "share_number": self.quantity,
                    "partner_id": self.partner_id_to.id,
                    "share_product_id": self.share_product_id.id,
                    "share_unit_price": self.share_unit_price,
                    "effective_date": effective_date,
                }
            )
            values["partner_id_to"] = self.partner_id_to.id
        else:
            raise ValidationError(_("This operation is not yet" " implemented."))

        sequence_operation = self.env.ref(
            "easy_my_coop.sequence_register_operation", False
        )  # noqa
        sub_reg_operation = sequence_operation.next_by_id()

        values["name"] = sub_reg_operation
        values["register_number_operation"] = int(sub_reg_operation)

        self.write({"state": "done"})

        sub_register_line = self.env["subscription.register"].create(values)

        # send mail to the receiver
        if self.operation_type == "transfer":
            self._send_share_transfer_mail(sub_register_line)

        self._send_share_update_mail(sub_register_line)
