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

    def _prepare_portal_layout_values(self):
        values = super(CooperatorWebsiteAccount,
                       self)._prepare_portal_layout_values()
        # We assume that commercial_partner_id always point to the
        # partner itself or to the linked partner. So there is no
        # need to check if the partner is a "contact" or not.
        coop = request.env.user.partner_id.commercial_partner_id
        coop_bank = request.env['res.partner.bank'].sudo().search(
            [('partner_id', 'in', [coop.id])],
            limit=1
        )
        values.update({
            'coop': coop,
            'coop_bank': coop_bank,
        })
        return values

    @http.route()
    def account(self):
        """ Add Release Capital Request to main account page """
        response = super(CooperatorWebsiteAccount, self).account()
        partner = request.env.user.partner_id

        invoice_mgr = request.env['account.invoice']
        capital_request_count = invoice_mgr.search_count([
            ('message_partner_ids', 'in',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancelled']),
            # Get only the release capital request
            ('release_capital_request', '=', True),
        ])

        response.qcontext.update({
            'capital_request_count': capital_request_count,
        })
        return response

    @http.route(
        ['/my/release_capital_request',
         '/my/release_capital_request/page/<int:page>'],
        type='http', auth="user", website=True)
    def portal_my_release_capital_request(self, page=1, date_begin=None,
                                          date_end=None, **kw):
        """Render a page with the list of release capital request.
        A release capital request is an invoice with a flag that tell
        if it's a capital request or not.
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        invoice_mgr = request.env['account.invoice']

        domain = [
            ('message_partner_ids', 'in',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancelled']),
            # Get only the release capital request
            ('release_capital_request', '=', True),
        ]
        archive_groups = self._get_archive_groups('account.invoice', domain)
        if date_begin and date_end:
            domain += [('create_date', '>=', date_begin),
                       ('create_date', '<', date_end)]

        # count for pager
        capital_request_count = invoice_mgr.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/release_capital_request",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=capital_request_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = invoice_mgr.search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'capital_requests': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/release_capital_request',
        })
        return request.website.render(
            "easy_my_coop_website_portal.portal_my_capital_releases",
            values
        )

    @http.route(['/my/cooperator_certificat/send'],
                type='http', auth="user", website=True)
    def send_cooperator_certificat(self, **kw):
        partner = request.env.user.partner_id
        certificat_email_template = request.env.ref(
            'easy_my_coop.email_template_certificat_increase', False
        ).sudo()
        if certificat_email_template:
            certificat_email_template.send_mail(
                partner.commercial_partner_id.id
            )
        return request.redirect(kw['nexturl'])
