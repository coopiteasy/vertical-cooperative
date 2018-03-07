# -*- coding: utf-8 -*-

# Copyright 2015-2016 Odoo S.A.
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import fields, models, http
from openerp.http import request
from openerp import tools
from openerp.tools.translate import _

from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount


class CooperatorWebsiteAccount(WebsiteAccount):

    @http.route()
    def account(self):
        """ Add Tax Shelter Certificate to main account page """
        response = super(CooperatorWebsiteAccount, self).account()
        partner = request.env.user.partner_id

        tax_shelter_mgr = request.env['tax.shelter.certificate'].sudo()
        tax_shelter_count = tax_shelter_mgr.search_count([
            ('partner_id', 'in', [partner.commercial_partner_id.id]),
        ])

        response.qcontext.update({
            'tax_shelter_count': tax_shelter_count,
        })
        return response

    @http.route(
        ['/my/tax_shelter_certificate',
         '/my/tax_shelter_certificate/page/<int:page>'],
        type='http', auth="user", website=True)
    def portal_my_tax_shelter_certificate(self, page=1, date_begin=None,
                                          date_end=None, **kw):
        """Render a page that lits the tax shelter report:
            * Subscriptions Certificates
            * Shares Certifcates
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        tax_shelter_mgr = request.env['tax.shelter.certificate'].sudo()

        domain = [
            ('partner_id', 'in', [partner.commercial_partner_id.id]),
        ]

        if date_begin and date_end:
            domain += [('create_date', '>=', date_begin),
                       ('create_date', '<', date_end)]

        # count for pager
        tax_shelter_count = tax_shelter_mgr.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/tax_shelter_certificate",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=tax_shelter_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        tax_shelters = tax_shelter_mgr.search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'tax_shelters': tax_shelters,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/tax_shelter_certificate',
        })
        return request.website.render(
            "easy_my_coop_website_taxshelter.portal_my_tax_shelter",
            values
        )
