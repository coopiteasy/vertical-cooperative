# -*- coding: utf-8 -*-

# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# Copyright 2018 Odoo SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import fields, models, http
from openerp.http import request
from openerp import tools
from openerp.tools.translate import _

from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount


class ExtendWebsiteAccountController(WebsiteAccount):

    mandatory_billing_fields = [
        "name",
        "phone",
        "email",
        "city",
        "country_id",
        "street",
    ]
    optional_billing_fields = [
        "zipcode",
        "state_id",
        "vat",
    ]

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def details(self, redirect=None, **post):
        partner = request.env['res.users'].browse(request.uid).partner_id
        values = {
            'error': {},
            'error_message': []
        }

        self._set_mandatory_fields(post)
        self._set_optional_fields(post)

        all_fields = (
            self.mandatory_billing_fields
            + self.optional_billing_fields
        )

        if post:
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                # Change zipcode to zip as it is stored as zip in the
                # partner
                if 'zipcode' in all_fields:
                    post.update({'zip': post.pop('zipcode', '')})

                if partner.type == "contact":
                    address_fields = {}
                    if 'city' in all_fields:
                        address_fields.update({
                            'city': post.pop('city'),
                        })
                    if 'street' in all_fields:
                        address_fields.update({
                            'street': post.pop('street'),
                        })
                    if 'vat' in all_fields:
                        address_fields.update({
                            'vat': post['vat'],
                        })
                    if 'zipcode' in all_fields:
                        address_fields.update({
                            'zip': post.pop('zip'),
                        })
                    if 'country_id' in all_fields:
                        address_fields.update({
                            'country_id': post.pop('country_id'),
                        })
                    if 'state_id' in all_fields:
                        address_fields.update({
                            'state_id': post.pop('state_id')
                        })

                    company_fields = {}
                    if 'company_name' in all_fields:
                        company_fields.update({
                            'name': post.pop('company_name'),
                        })
                    if 'vat' in all_fields:
                        company_fields.update({
                            # The VAT must be updated on the company and on
                            # the partner, so pop is not used.
                            'vat': post['vat'],
                        })

                    partner.commercial_partner_id.sudo().write(address_fields)
                    partner.commercial_partner_id.sudo().write(company_fields)
                # Write the rest of the info in the partner
                partner.sudo().write(post)

                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
        })

        return request.website.render("website_portal.details", values)

    def _set_mandatory_fields(self, data):
        """Change mandatory billing fields of the form.
        Overwrite this function if mandatory fields must be changed
        depending on the value of the data or any other value.
        Here it mark the field 'company_name' as need or not depending
        on the current user.
        """
        partner = request.env['res.users'].browse(request.uid).partner_id
        if (partner.parent_id
                and 'company_name' not in self.mandatory_billing_fields):
            self.mandatory_billing_fields.append('company_name')
        if (not partner.parent_id
                and 'company_name' in self.mandatory_billing_fields):
            self.mandatory_billing_fields.remove('company_name')

    def _set_optional_fields(self, data):
        """Same as set_mandatory_fields but for optional ones.
        Here this does nothing.
        """
        pass

    def details_form_validate(self, data):
        """Validate the form"""
        error = dict()
        error_message = []

        all_fields = (
            self.mandatory_billing_fields
            + self.optional_billing_fields
        )

        # Validation
        for field_name in self.mandatory_billing_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if ('email' in all_fields
                and data.get('email')
                and not tools.single_email_re.match(data.get('email'))):
            error["email"] = 'error'
            error_message.append(
                _('Invalid Email! Please enter a valid email address.')
            )

        # vat validation
        if ('vat' in all_fields
                and data.get("vat")
                and hasattr(request.env["res.partner"], "check_vat")):
            if request.website.company_id.vat_check_vies:
                # force full VIES online check
                check_func = request.env["res.partner"].vies_vat_check
            else:
                # quick and partial off-line checksum validation
                check_func = request.env["res.partner"].simple_vat_check
            vat_country, vat_number = request.env["res.partner"]._split_vat(
                data.get("vat")
            )
            if not check_func(vat_country, vat_number):  # simple_vat_check
                error["vat"] = 'error'
        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data.iterkeys() if k not in all_fields]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message
