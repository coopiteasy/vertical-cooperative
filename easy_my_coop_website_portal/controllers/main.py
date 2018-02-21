# -*- coding: utf-8 -*-

# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# Copyright 2018 Odoo SA
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
        coop_bank = request.env['res.partner.bank'].search(
            [('partner_id', '=', coop.id)],
            limit=1
        )
        values.update({
            'coop': coop,
            'coop_bank': coop_bank,
        })
        return values


