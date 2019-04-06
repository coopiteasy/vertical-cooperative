# -*- coding: utf-8 -*-
from openerp import models, fields, api


class RecomputeWizard(models.TransientModel):
    _name = 'register.number.wizard'

    from_number = fields.Integer(string="From number")
    to_number = fields.Integer(string="To number")

    @api.one
    def compute_register_number(self):
        obj_sequence = self.env['ir.sequence']
        sub_reg_obj = self.env['subscription.register']

        sequence_operation = obj_sequence.search([('name', '=', 'Register Operation')])[0]
        subscription_registers = sub_reg_obj.search([('register_number_operation', '>=', self.from_number)])
        for subscription_register in subscription_registers:
            sub_reg_operation = sequence_operation.next_by_id()

            subscription_register.write({'name': sub_reg_operation,
                                         'register_number_operation': int(sub_reg_operation)})
