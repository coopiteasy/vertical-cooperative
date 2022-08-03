# Copyright 2017-2018 Coop IT Easy SCRLfs <remy@gcoopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import http
from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount
from openerp.exceptions import AccessError, MissingError
from openerp.http import request
from werkzeug.exceptions import Forbidden, NotFound


class TaxShelterWebsiteAccount(WebsiteAccount):
    @http.route()
    def account(self):
        """ Add Tax Shelter Certificate to main account page """
        response = super(TaxShelterWebsiteAccount, self).account()
        partner = request.env.user.partner_id

        tax_shelter_mgr = request.env["tax.shelter.certificate"]
        tax_shelter_count = tax_shelter_mgr.sudo().search_count(
            [("partner_id", "in", [partner.commercial_partner_id.id])]
        )

        response.qcontext.update({"tax_shelter_count": tax_shelter_count})
        return response

    @http.route(
        [
            "/my/tax_shelter_certificate",
            "/my/tax_shelter_certificate/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tax_shelter_certificate(
        self, page=1, date_begin=None, date_end=None, **kw
    ):
        """Render a page that lits the tax shelter report:
            * Tax Shelter Certificates
            * Shares Certifcates
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        tax_shelter_mgr = request.env["tax.shelter.certificate"]

        domain = [("partner_id", "in", [partner.commercial_partner_id.id])]

        if date_begin and date_end:
            domain += [
                ("create_date", ">=", date_begin),
                ("create_date", "<", date_end),
            ]

        # count for pager
        tax_shelter_count = tax_shelter_mgr.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/tax_shelter_certificate",
            url_args={"date_begin": date_begin, "date_end": date_end},
            total=tax_shelter_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        tax_shelters = tax_shelter_mgr.sudo().search(
            domain, limit=self._items_per_page, offset=pager["offset"]
        )
        tax_shelters = tax_shelters.sorted(
            key=lambda r: r.declaration_id.fiscal_year, reverse=True
        )
        values.update(
            {
                "date": date_begin,
                "tax_shelters": tax_shelters,
                "page_name": "invoice",
                "pager": pager,
                "default_url": "/my/tax_shelter_certificate",
            }
        )
        return request.website.render(
            "easy_my_coop_website_taxshelter.portal_my_tax_shelter", values
        )

    @http.route(
        ["/my/taxshelter_certificate/pdf/<int:oid>"],
        type="http",
        auth="user",
        website=True,
    )
    def get_taxshelter_certificate_pdf(self, oid=-1):
        """Render the Tax Shelter Certificate pdf of the given Tax
        Shelter Report
        """
        # Get the subscription certificate and raise an error if the user
        # is not allowed to access to it or if the object is not found.
        partner = request.env.user.partner_id
        tax_shelter_mgr = request.env["tax.shelter.certificate"]
        tax_shelter = tax_shelter_mgr.sudo().browse(oid)
        try:
            if tax_shelter.partner_id != partner:
                raise Forbidden()
        except AccessError:
            raise Forbidden()
        except MissingError:
            raise NotFound()
        # Get the pdf
        report_mgr = request.env["report"]
        pdf = report_mgr.sudo().get_pdf(
            tax_shelter,
            "easy_my_coop_taxshelter_report.tax_shelter_subscription_report",
        )
        filename = "Tax Shelter Certificate - {} - {}".format(
            partner.name, tax_shelter.declaration_id.fiscal_year
        )
        return self._render_pdf(pdf, filename)

    @http.route(
        ["/my/share_certificate/pdf/<int:oid>"],
        type="http",
        auth="user",
        website=True,
    )
    def get_share_certificate_pdf(self, oid=-1):
        """Render the Share Certificate pdf of the given Tax Shelter
        Report
        """
        # Get the share certificate and raise an error if the user
        # is not allowed to access to it or if the object is not found.
        partner = request.env.user.partner_id
        tax_shelter_mgr = request.env["tax.shelter.certificate"]
        tax_shelter = tax_shelter_mgr.sudo().browse(oid)
        try:
            if tax_shelter.partner_id != partner:
                raise Forbidden()
        except AccessError:
            raise Forbidden()
        except MissingError:
            raise NotFound()
        # Get the pdf
        report_mgr = request.env["report"]
        pdf = report_mgr.sudo().get_pdf(
            tax_shelter,
            "easy_my_coop_taxshelter_report.tax_shelter_shares_report",
        )
        filename = "Share Certificate - {} - {}".format(
            partner.name, tax_shelter.declaration_id.fiscal_year
        )
        return self._render_pdf(pdf, filename)

    def _render_pdf(self, pdf, filename):
        """Render a http response for a pdf"""
        pdfhttpheaders = [
            ("Content-Disposition", 'inline; filename="%s.pdf"' % filename),
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
