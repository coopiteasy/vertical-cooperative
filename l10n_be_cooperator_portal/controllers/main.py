# Copyright 2017-2018 Coop IT Easy SC <remy@gcoopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PortalTaxShelter(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        tax_shelter_count = (
            request.env["tax.shelter.certificate"]
            .sudo()
            .search_count([("partner_id", "in", [partner.commercial_partner_id.id])])
        )
        values["tax_shelter_count"] = tax_shelter_count
        return values

    def _taxshelter_certificate_get_page_view_values(
        self, taxshelter_certificate, access_token, **kwargs
    ):
        values = {
            "company_id": request.env.company,
            "page_name": "taxshelter",
            "taxshelter": taxshelter_certificate,
        }
        return self._get_page_view_values(
            taxshelter_certificate,
            access_token,
            values,
            "my_taxshelter_certificates_history",
            False,
            **kwargs,
        )

    @http.route(
        [
            "/my/tax_shelter_certificates",
            "/my/tax_shelter_certificates/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tax_shelter_certificates(
        self, page=1, date_begin=None, date_end=None, **kw
    ):
        """Render a page that lits the tax shelter report:
        * Tax Shelter Certificates
        * Shares Certifcates
        """
        values = self._prepare_portal_layout_values()
        TaxShelterCertificate = request.env["tax.shelter.certificate"]
        partner = request.env.user.partner_id
        domain = [("partner_id", "in", [partner.commercial_partner_id.id])]

        if date_begin and date_end:
            domain += [
                ("create_date", ">=", date_begin),
                ("create_date", "<", date_end),
            ]

        # count for pager
        tax_shelter_count = TaxShelterCertificate.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tax_shelter_certificates",
            url_args={"date_begin": date_begin, "date_end": date_end},
            total=tax_shelter_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        tax_shelters = TaxShelterCertificate.sudo().search(
            domain, limit=self._items_per_page, offset=pager["offset"]
        )
        tax_shelters = tax_shelters.sorted(
            key=lambda r: r.declaration_id.fiscal_year, reverse=True
        )
        request.session["my_taxshelter_certificates_history"] = tax_shelters.ids[:100]

        values.update(
            {
                "company_id": request.env.company,
                "date": date_begin,
                "tax_shelters": tax_shelters,
                "page_name": "taxshelter",
                "pager": pager,
                "default_url": "/my/tax_shelter_certificates",
            }
        )
        return request.render("l10n_be_cooperator_portal.portal_my_tax_shelter", values)

    # Black adds a trailing comma after last argument of function definition
    #  this syntax is invalid for python < 3.6
    # Exclude for formatting while not fixed, follow status here:
    # https://github.com/psf/black/issues/1657
    # fmt: off
    @http.route(
        ["/my/tax_shelter_certificates/<int:certificate_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_taxshelter_certificate(
        self,
        certificate_id,
        access_token=None,
        report_type=None,
        download=False,
        query_string=None,
        **kw
    ):
        # fmt: on
        partner = request.env.user.partner_id
        try:
            taxshelter_certificate_sudo = self._document_check_access(
                "tax.shelter.certificate", certificate_id, access_token
            )
            if taxshelter_certificate_sudo.partner_id != partner:
                raise Forbidden()
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text") and query_string in (
            "subscription",
            "shares",
        ):
            report_ref = (
                "l10n_be_cooperator.action_tax_shelter_%s_report"
                % (query_string)
            )
            return self._show_report(
                model=taxshelter_certificate_sudo,
                report_type=report_type,
                report_ref=report_ref,
                download=download,
            )

        values = self._taxshelter_certificate_get_page_view_values(
            taxshelter_certificate_sudo, access_token, **kw
        )
        return request.render(
            "l10n_be_cooperator_portal.portal_taxshelter_page", values
        )
