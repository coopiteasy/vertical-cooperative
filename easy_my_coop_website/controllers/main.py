import base64
from datetime import datetime
import re

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

# Only use for behavior, don't stock it
_TECHNICAL = ['view_from', 'view_callback']
# Allow in description
_BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date',
              'user_id', 'active']

_COOP_FORM_FIELD = ['email',  'confirm_email', 'firstname', 'lastname',
                    'birthdate', 'iban', 'share_product_id',
                    'address', 'city', 'zip_code', 'country_id', 'phone',
                    'lang', 'nb_parts', 'total_parts', 'error_msg']

_COMPANY_FORM_FIELD = ['is_company', 'company_register_number', 'company_name',
                       'company_email', 'confirm_email', 'email', 'firstname',
                       'lastname', 'birthdate', 'iban', 'share_product_id',
                       'address', 'city', 'zip_code', 'country_id', 'phone',
                       'lang', 'nb_parts', 'total_parts', 'error_msg',
                       'company_type']


class WebsiteSubscription(http.Controller):

    @http.route(['/page/become_cooperator',
                 '/become_cooperator'],
                type='http', auth="public", website=True)
    def display_become_cooperator_page(self, **kwargs):
        values = {}
        logged = False
        if request.env.user.login != 'public':
            logged = True
            partner = request.env.user.partner_id
            if partner.is_company:
                return self.display_become_company_cooperator_page()
        values = self.fill_values(values, False, logged, True)

        for field in _COOP_FORM_FIELD:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)

        values.update(kwargs=kwargs.items())
        return request.render("easy_my_coop_website.becomecooperator", values)

    @http.route(['/page/become_company_cooperator',
                 '/become_company_cooperator'],
                type='http', auth="public", website=True)
    def display_become_company_cooperator_page(self, **kwargs):
        values = {}
        logged = False

        if request.env.user.login != 'public':
            logged = True
        values = self.fill_values(values, True, logged, True)

        for field in _COMPANY_FORM_FIELD:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.render("easy_my_coop_website.becomecompanycooperator",
                              values)

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        return {
            '_values': values,
            '_kwargs': kwargs,
        }

    def get_subscription_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.render("easy_my_coop_website.cooperator_thanks", values)

    def get_date_string(self, birthdate):
        if birthdate:
            return datetime.strftime(birthdate, "%d/%m/%Y")
        return False

    def get_values_from_user(self, values, is_company):
        # the subscriber is connected
        if request.env.user.login != 'public':
            values['logged'] = 'on'
            partner = request.env.user.partner_id

            if partner.member or partner.old_member:
                values['already_cooperator'] = 'on'
            if partner.bank_ids:
                values['iban'] = partner.bank_ids[0].acc_number
            values['address'] = partner.street
            values['zip_code'] = partner.zip
            values['city'] = partner.city
            values['country_id'] = partner.country_id.id

            if is_company:
                # company values
                values['company_register_number'] = partner.company_register_number
                values['company_name'] = partner.name
                values['company_email'] = partner.email
                values['company_type'] = partner.legal_form
                # contact person values
                representative = partner.get_representative()
                values['firstname'] = representative.firstname
                values['lastname'] = representative.lastname
                values['gender'] = representative.gender
                values['email'] = representative.email
                values['contact_person_function'] = representative.function
                values['birthdate'] = self.get_date_string(representative.birthdate_date)
                values['lang'] = representative.lang
                values['phone'] = representative.phone
            else:
                values['firstname'] = partner.firstname
                values['lastname'] = partner.lastname
                values['email'] = partner.email
                values['gender'] = partner.gender
                values['birthdate'] = self.get_date_string(partner.birthdate_date)
                values['lang'] = partner.lang
                values['phone'] = partner.phone
        return values

    def fill_values(self, values, is_company, logged, load_from_user=False):
        sub_req_obj = request.env['subscription.request']
        company = request.website.company_id
        products = self.get_products_share(is_company)

        if load_from_user:
            values = self.get_values_from_user(values, is_company)
        if is_company:
            values['is_company'] = 'on'
        if logged:
            values['logged'] = 'on'
        values['countries'] = self.get_countries()
        values['langs'] = self.get_langs()
        values['products'] = products
        fields_desc = sub_req_obj.sudo().fields_get(['company_type', 'gender'])
        values['company_types'] = fields_desc['company_type']['selection']
        values['genders'] = fields_desc['gender']['selection']
        values['company'] = company

        if not values.get('share_product_id'):
            for product in products:
                if product.default_share_product is True:
                    values['share_product_id'] = product.id
                    break
            if not values.get('share_product_id', False) and products:
                values['share_product_id'] = products[0].id
        if not values.get('country_id'):
            if company.default_country_id:
                values['country_id'] = company.default_country_id.id
            else:
                values['country_id'] = '21'
        if not values.get('activities_country_id'):
            if company.default_country_id:
                values['activities_country_id'] = company.default_country_id.id
            else:
                values['activities_country_id'] = '21'
        if not values.get('lang'):
            if company.default_lang_id:
                values['lang'] = company.default_lang_id.code

        comp = request.env['res.company']._company_default_get()
        values.update({
            'display_data_policy': comp.display_data_policy_approval,
            'data_policy_required': comp.data_policy_approval_required,
            'data_policy_text': comp.data_policy_approval_text,
            'display_internal_rules': comp.display_internal_rules_approval,
            'internal_rules_required': comp.internal_rules_approval_required,
            'internal_rules_text': comp.internal_rules_approval_text,
        })
        return values

    def get_products_share(self, is_company):
        product_obj = request.env['product.template']
        products = product_obj.sudo().get_web_share_products(is_company)

        return products

    def get_countries(self):
        countries = request.env['res.country'].sudo().search([])

        return countries

    def get_langs(self):
        langs = request.env['res.lang'].sudo().search([])
        return langs

    def get_selected_share(self, kwargs):
        prod_obj = request.env['product.template']
        product_id = kwargs.get("share_product_id")
        return prod_obj.sudo().browse(int(product_id)).product_variant_ids[0]

    def validation(self, kwargs, logged, values, post_file):
        user_obj = request.env['res.users']
        sub_req_obj = request.env['subscription.request']

        redirect = "easy_my_coop_website.becomecooperator"

        email = kwargs.get('email')
        is_company = kwargs.get("is_company") == 'on'

        if is_company:
            is_company = True
            redirect = "easy_my_coop_website.becomecompanycooperator"
            email = kwargs.get('company_email')

        if 'g-recaptcha-response' not in kwargs or kwargs['g-recaptcha-response'] == '':
            values = self.fill_values(values, is_company, logged)
            values.update(kwargs)
            values["error_msg"] = _("the captcha has not been validated,"
                                    " please fill in the captcha")

            return request.render(redirect, values)
        elif not request.website.is_captcha_valid(
                    kwargs['g-recaptcha-response']):
            values = self.fill_values(values, is_company, logged)
            values.update(kwargs)
            values["error_msg"] = _("the captcha has not been validated,"
                                    " please fill in the captcha")

            return request.render(redirect, values)

        # Check that required field from model subscription_request exists
        required_fields = sub_req_obj.sudo().get_required_field()
        error = set(field for field in required_fields if not values.get(field)) #noqa

        if error:
            values = self.fill_values(values, is_company, logged)
            values["error_msg"] = _("Some mandatory fields have not "
                                    "been filled")
            values = dict(values, error=error, kwargs=kwargs.items())
            return request.render(redirect, values)

        if not logged and email:
            user = user_obj.sudo().search([('login', '=', email)])
            if user:
                values = self.fill_values(values, is_company, logged)
                values.update(kwargs)
                values["error_msg"] = _("There is an existing account for this"
                                        " mail address. Please login before "
                                        "fill in the form")

                return request.render(redirect, values)
            else:
                confirm_email = kwargs.get('confirm_email')
                if email != confirm_email:
                    values = self.fill_values(values, is_company, logged)
                    values.update(kwargs)
                    values["error_msg"] = _("The email and the confirmation "
                                            "email doesn't match.Please check "
                                            "the given mail addresses")
                    return request.render(redirect, values)

        company = request.website.company_id
        if company.allow_id_card_upload:
            if not post_file:
                values = self.fill_values(values, is_company, logged)
                values.update(kwargs)
                values["error_msg"] = _("You need to upload a"
                                        " scan of your id card")
                return request.render(redirect, values)

        iban = kwargs.get("iban")
        valid = sub_req_obj.check_iban(iban)

        if not valid:
            values = self.fill_values(values, is_company, logged)
            values["error_msg"] = _("You iban account number"
                                    "is not valid")
            return request.render(redirect, values)

        # check the subscription's amount
        max_amount = company.subscription_maximum_amount
        if logged:
            partner = request.env.user.partner_id
            if partner.member:
                max_amount = max_amount - partner.total_value
                if company.unmix_share_type:
                    share = self.get_selected_share(kwargs)
                    if partner.cooperator_type != share.default_code:
                        values = self.fill_values(values, is_company, logged)
                        values["error_msg"] = (_("You can't subscribe two "
                                                 "different types of share"))
                        return request.render(redirect, values)
        total_amount = float(kwargs.get('total_parts'))

        if max_amount > 0 and total_amount > max_amount:
            values = self.fill_values(values, is_company, logged)
            values["error_msg"] = (_("You can't subscribe for an amount that "
                                     "exceed ")
                                   + str(max_amount)
                                   + company.currency_id.symbol)
            return request.render(redirect, values)
        return True

    @http.route(['/subscription/get_share_product'],
                type='json',
                auth="public",
                methods=['POST'], website=True)
    def get_share_product(self, share_product_id, **kw):
        product_template = request.env['product.template']
        product = product_template.sudo().browse(int(share_product_id))
        return {
            product.id: {
                'list_price': product.list_price,
                'min_qty': product.minimum_quantity,
                'force_min_qty': product.force_min_qty
                }
            }

    @http.route(['/subscription/subscribe_share'],
                type='http',
                auth="public", website=True)
    def share_subscription(self, **kwargs):
        sub_req_obj = request.env['subscription.request']
        attach_obj = request.env['ir.attachment']

        # List of file to add to ir_attachment once we have the ID
        post_file = []
        # Info to add after the message
        post_description = []
        values = {}

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif (field_name in sub_req_obj._fields
                    and field_name not in _BLACKLIST):
                values[field_name] = field_value
            # allow to add some free fields or blacklisted field like ID
            elif field_name not in _TECHNICAL:
                post_description.append("%s: %s" % (field_name, field_value))

        logged = kwargs.get("logged") == 'on'
        is_company = kwargs.get("is_company") == 'on'

        response = self.validation(kwargs, logged, values, post_file)
        if response is not True:
            return response

        already_coop = False
        if logged:
            partner = request.env.user.partner_id
            values['partner_id'] = partner.id
            already_coop = partner.member
        elif kwargs.get("already_cooperator") == 'on':
            already_coop = True

        values["already_cooperator"] = already_coop
        values["is_company"] = is_company

        if kwargs.get('data_policy_approved', 'off') == 'on':
            values['data_policy_approved'] = True

        if kwargs.get('internal_rules_approved', 'off') == 'on':
            values['internal_rules_approved'] = True

        lastname = kwargs.get("lastname").upper()
        firstname = kwargs.get("firstname").title()

        values["name"] = firstname + " " + lastname
        values["lastname"] = lastname
        values["firstname"] = firstname
        values["birthdate"] = datetime.strptime(kwargs.get("birthdate"),
                                                "%d/%m/%Y").date()
        values["source"] = "website"

        values["share_product_id"] = self.get_selected_share(kwargs).id

        if is_company:
            if kwargs.get("company_register_number", is_company):
                values["company_register_number"] = re.sub('[^0-9a-zA-Z]+',
                                                           '',
                                                           kwargs.get("company_register_number"))
            subscription_id = sub_req_obj.sudo().create_comp_sub_req(values)
        else:
            subscription_id = sub_req_obj.sudo().create(values)

        if subscription_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'subscription.request',
                    'res_id': subscription_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                attach_obj.sudo().create(attachment_value)

        return self.get_subscription_response(values, kwargs)
