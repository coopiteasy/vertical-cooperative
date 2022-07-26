from odoo import api, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    @api.multi
    def send_mail_with_multiple_attachments(
        self,
        res_id,
        additional_attachments,
        force_send=False,
        raise_exception=False,
    ):
        """Generates a new mail message for the given template and record,
        and schedules it for delivery through the ``mail``
        module's scheduler.

        :param int res_id: id of the record to render the template with
                           (model is taken from the template)
        :param bool force_send: if True, the generated mail.message is
             immediately sent after being created, as if the scheduler
             was executed for this message only.
        :returns: id of the mail.message that was created
        """
        self.ensure_one()
        Mail = self.env["mail.mail"]
        # TDE FIXME: should remove dfeault_type from context
        Attachment = self.env["ir.attachment"]

        # create a mail_mail based on values, without attachments
        values = self.generate_email(res_id)
        values["recipient_ids"] = [
            (4, pid) for pid in values.get("partner_ids", list())
        ]
        attachment_ids = values.pop("attachment_ids", [])
        attachments = values.pop("attachments", [])
        # add a protection against void email_from
        if "email_from" in values and not values.get("email_from"):
            values.pop("email_from")
        mail = Mail.create(values)

        # manage attachments
        attachments.extend(additional_attachments)
        for attachment in attachments:
            attachment_data = {
                "name": attachment[0],
                "datas_fname": attachment[0],
                "datas": attachment[1],
                "res_model": "mail.message",
                "res_id": mail.mail_message_id.id,
            }
            attachment_ids.append(Attachment.create(attachment_data).id)
        if attachment_ids:
            values["attachment_ids"] = [(6, 0, attachment_ids)]
            mail.write({"attachment_ids": [(6, 0, attachment_ids)]})

        if force_send:
            mail.send(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?
