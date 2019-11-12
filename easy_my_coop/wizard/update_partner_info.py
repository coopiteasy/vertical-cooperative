from odoo import api, fields, models


class PartnerUpdateInfo(models.TransientModel):
    _name = "partner.update.info"
    _description = "Update Partner Info"

    @api.model
    def _get_partner(self):
        active_id = self.env.context.get('active_id')
        return self.env['res.partner'].browse(active_id)

    @api.model
    def _get_register_number(self):
        partner = self._get_partner()
        if partner.is_company:
            return partner.company_register_number

    @api.model
    def _get_is_company(self):
        return self._get_partner().is_company

    is_company = fields.Boolean(string="Is company",
                                default=_get_is_company)
    register_number = fields.Char(string="Register Company Number",
                                  default=_get_register_number)
    cooperator = fields.Many2one('res.partner',
                                 string="Cooperator",
                                 default=_get_partner)
    all = fields.Boolean(string="Update from subscription request")
    birthdate = fields.Boolean(string="Set missing birth date")
    legal_form = fields.Boolean(string="Set legal form")
    representative_function = fields.Boolean(string="Set function")

    @api.multi
    def update(self):
        partner_obj = self.env['res.partner']
        cooperator = self.cooperator
        coop_vals = {}

        if self.all:
            if self.legal_form or self.representative_function:
                coops = partner_obj.search([('cooperator', '=', True),
                                            ('is_company', '=', True)])
                for coop in coops:
                    coop_vals = {}
                    sub_reqs = coop.subscription_request_ids.filtered(lambda r: r.state in ['done', 'paid'])
                    if sub_reqs:
                        sub_req = sub_reqs[0]
                        if self.legal_form:
                            coop_vals['legal_form'] = sub_req.company_type
                            coop.write(coop_vals)
                        if self.representative_function:
                            contact = coop.get_representative()
                            contact.function = sub_req.contact_person_function
            else:
                coops = partner_obj.search([('cooperator', '=', True),
                                            ('birthdate_date', '=', False),
                                            ('is_company', '=', False)])
                for coop in coops:
                    coop_vals = {}
                    sub_reqs = coop.subscription_request_ids.filtered(lambda r: r.state in ['done', 'paid'])
                    if sub_reqs:
                        sub_req = sub_reqs[0]
                        if self.birthdate:
                            coop_vals['birthdate_date'] = sub_req.birthdate
                        coop.write(coop_vals)
        else:
            if cooperator:
                if cooperator.is_company:
                    coop_vals['company_register_number'] = self.register_number
                if coop_vals:
                    cooperator.write(coop_vals)

        return True
