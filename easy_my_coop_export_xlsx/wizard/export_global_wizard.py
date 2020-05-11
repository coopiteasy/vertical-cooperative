import base64
import time

import xlsxwriter
from cStringIO import StringIO
from openerp import api, fields, models

HEADER = [
    "Num. Coop",
    "Nom",
    "Email",
    "Banque",
    "Mobile",
    "Adresse",
    "Rue",
    "Code Postal",
    "Ville",
    "Pays",
    "Nombre de part total",
    "Montant total des parts",
    "Demande de liberation de capital",
    "Communication",
    "Nombre de part",
    "Montant",
    "Reception du paiement",
    "Date de la souscription",
]
HEADER2 = [
    "Date de la souscription",
    "Nom",
    "Type",
    "Nombre de part",
    "Montant",
    "Statut",
    "Email",
    "Mobile",
    "Adresse",
    "Code Postal",
    "Ville",
    "Pays",
]


class ExportGlobalReport(models.TransientModel):
    _name = "export.global.report"

    name = fields.Char("Name")

    def write_header(self, worksheet, headers):
        i = 0
        for header in headers:
            worksheet.write(0, i, header)
            i += 1
        return True

    @api.multi
    def export_global_report_xlsx(self):
        partner_obj = self.env["res.partner"]
        invoice_obj = self.env["account.invoice"]
        subscription_obj = self.env["subscription.request"]

        file_data = StringIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet1 = workbook.add_worksheet()

        self.write_header(worksheet1, HEADER)
        cooperators = partner_obj.search(
            [("cooperator", "=", True), ("member", "=", True)]
        )

        j = 1
        for coop in cooperators:
            i = 0
            worksheet1.write(j, i, coop.cooperator_register_number)
            i += 1
            worksheet1.write(j, i, coop.name)
            i += 1
            worksheet1.write(j, i, coop.email)
            i += 1
            acc_number = ""
            if coop.bank_ids:
                acc_number = coop.bank_ids[0].acc_number
            worksheet1.write(j, i, acc_number)
            i += 1
            worksheet1.write(j, i, coop.phone)
            i += 1
            address = (
                coop.street
                + " "
                + coop.zip
                + " "
                + coop.city
                + " "
                + coop.country_id.name
            )
            worksheet1.write(j, i, address)
            i += 1
            worksheet1.write(j, i, coop.street)
            i += 1
            worksheet1.write(j, i, int(coop.zip))
            i += 1
            worksheet1.write(j, i, coop.city)
            i += 1
            worksheet1.write(j, i, coop.country_id.name)
            i += 1
            worksheet1.write(j, i, coop.number_of_share)
            i += 1
            worksheet1.write(j, i, coop.total_value)

            invoice_ids = invoice_obj.search(
                [
                    ("release_capital_request", "=", True),
                    ("partner_id", "=", coop.id),
                ]
            )
            j += 1
            for invoice in invoice_ids:
                i = 11
                worksheet1.write(j, i, invoice.number)
                i += 1
                worksheet1.write(j, i, invoice.state)
                i += 1
                worksheet1.write(j, i, invoice.date_invoice)
                i += 1
                worksheet1.write(j, i, invoice.reference)
                i += 1
                for line in invoice.invoice_line_ids:
                    worksheet1.write(j, i, line.quantity)
                    i += 1
                    worksheet1.write(j, i, line.price_subtotal)
                    i += 1
                if invoice.payment_ids:
                    worksheet1.write(j, i, invoice.payment_ids[0].payment_date)
                i += 1
                if invoice.subscription_request:
                    ind = len(invoice.subscription_request) - 1
                    worksheet1.write(
                        j, i, invoice.subscription_request[ind].date
                    )
                j += 1

            sub_requests = subscription_obj.search(
                [
                    ("state", "in", ["draft", "waiting"]),
                    ("partner_id", "=", coop.id),
                ]
            )
            for sub_request in sub_requests:
                i = 11
                worksheet1.write(
                    j,
                    i,
                    dict(subscription_obj._columns["type"].selection).get(
                        sub_request.type, False
                    ),
                )
                i += 1
                worksheet1.write(j, i, sub_request.state)
                i += 3
                quantity = int(sub_request.ordered_parts)
                worksheet1.write(j, i, quantity)
                i += 1
                amount = quantity * sub_request.share_unit_price
                worksheet1.write(j, i, amount)
                i += 2
                worksheet1.write(j, i, sub_request.date)
                j += 1

        worksheet1bis = workbook.add_worksheet()
        self.write_header(worksheet1bis, HEADER)
        cooperators = partner_obj.search(
            [("cooperator", "=", True), ("member", "=", False)]
        )

        j = 1
        for coop in cooperators:
            i = 0
            worksheet1bis.write(j, i, coop.cooperator_register_number)
            i += 1
            worksheet1bis.write(j, i, coop.name)
            i += 1
            worksheet1bis.write(j, i, coop.email)
            i += 1
            worksheet1bis.write(j, i, coop.phone)
            i += 1
            worksheet1bis.write(j, i, coop.street)
            i += 1
            worksheet1bis.write(j, i, int(coop.zip))
            i += 1
            worksheet1bis.write(j, i, coop.city)
            i += 1
            worksheet1bis.write(j, i, coop.country_id.name)
            i += 1
            worksheet1bis.write(j, i, coop.number_of_share)
            i += 1
            worksheet1bis.write(j, i, coop.total_value)

            invoice_ids = invoice_obj.search(
                [
                    ("release_capital_request", "=", True),
                    ("partner_id", "=", coop.id),
                ]
            )
            j += 1
            for invoice in invoice_ids:
                i = 11
                worksheet1bis.write(j, i, invoice.number)
                i += 1
                worksheet1bis.write(j, i, invoice.state)
                i += 1
                worksheet1bis.write(j, i, invoice.date_invoice)
                i += 1
                worksheet1bis.write(j, i, invoice.reference)
                i += 1
                for line in invoice.invoice_line_ids:
                    worksheet1bis.write(j, i, line.quantity)
                    i += 1
                    worksheet1bis.write(j, i, line.price_subtotal)
                    i += 1
                if invoice.payment_ids:
                    worksheet1bis.write(j, i, invoice.payment_ids[0].date)
                i += 1
                if invoice.subscription_request:
                    ind = len(invoice.subscription_request) - 1
                    worksheet1bis.write(
                        j, i, invoice.subscription_request[ind].date
                    )
                j += 1

            sub_requests = subscription_obj.search(
                [
                    ("state", "in", ["draft", "waiting"]),
                    ("partner_id", "=", coop.id),
                ]
            )
            for sub_request in sub_requests:
                i = 11
                worksheet1bis.write(
                    j,
                    i,
                    dict(subscription_obj._columns["type"].selection).get(
                        sub_request.type, False
                    ),
                )
                i += 1
                worksheet1bis.write(j, i, sub_request.state)
                i += 3
                quantity = int(sub_request.ordered_parts)
                worksheet1bis.write(j, i, quantity)
                i += 1
                amount = quantity * sub_request.share_unit_price
                worksheet1bis.write(j, i, amount)
                i += 2
                worksheet1bis.write(j, i, sub_request.date)
                j += 1

        worksheet2 = workbook.add_worksheet()
        self.write_header(worksheet2, HEADER2)
        sub_requests = subscription_obj.search(
            [("state", "in", ["draft", "waiting"])]
        )

        j = 1
        for sub_request in sub_requests:
            i = 0
            worksheet2.write(j, i, sub_request.date)
            i += 1
            worksheet2.write(j, i, sub_request.name)
            i += 1
            sub_type_sel = subscription_obj._columns["type"].selection
            worksheet2.write(
                j, i, dict(sub_type_sel).get(sub_request.type, False)
            )
            i += 1
            quantity = int(sub_request.ordered_parts)
            worksheet2.write(j, i, quantity)
            i += 1
            amount = quantity * sub_request.share_unit_price
            worksheet2.write(j, i, amount)
            i += 1
            worksheet2.write(j, i, sub_request.state)
            i += 1
            worksheet2.write(j, i, sub_request.email)
            i += 1
            worksheet2.write(j, i, sub_request.phone)
            i += 1
            worksheet2.write(j, i, sub_request.address)
            i += 1
            worksheet2.write(j, i, sub_request.city)
            i += 1
            worksheet2.write(j, i, int(sub_request.zip_code))
            i += 1
            worksheet2.write(j, i, sub_request.country_id.name)
            j += 1

        workbook.close()
        file_data.seek(0)

        data = base64.encodestring(file_data.read())

        attachment_id = self.env["ir.attachment"].create(
            {
                "name": "Global export"
                + time.strftime("%Y-%m-%d %H:%M")
                + ".xlsx",
                "datas": data,
                "datas_fname": "Global_export.xlsx",
                "res_model": "export.global.report",
            }
        )

        # Prepare your download URL
        download_url = (
            "/web/content/" + str(attachment_id.id) + "?download=True"
        )
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
