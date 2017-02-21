# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Houssine BAKKALI
#    Copyright Open Architects Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _

class cooperative_report(models.TransientModel):
    _name = 'cooperative.history.report'
       
    def _print_report(self, data):
        
        return {'type': 'ir.actions.report.xml',
                'report_name': data['report'],
                'datas': data}
    
    def check_report(self):
        data = {}
        
        report_name = ''
        obj_ids = []
        if self._context.get('active_ids') : 
            data['ids'] = self._context.get('active_ids', [])
        else: 
            if self.report == 'coop_register':
                report_name = 'easy_my_coop.cooperator_register_G001'
                res_partner_obj = self.pool.get('res.partner')
                domain = []
                domain.append(('cooperator','=','True'))
                if self.display_cooperator == 'member' :
                    domain.append(('member','=','True'))
                obj_ids = res_partner_obj.search(cr,uid, domain, order='cooperator_register_number')    
            elif self.report == 'operation_register' :
                report_name = 'energiris_wp_sync.cooperator_subscription_G001'
                obj_ids = self.pool.get('subscription.register').search(cr,uid,[], order='register_number_operation')
            else : 
                raise osv.except_osv(_("Error!"), _("the report you've specified doesn't exist !"))
            
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['report'] = report_name 
        #data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to','display_time','display_cooperator','group_by_task','group_by_task_work'], context=context)[0]
        data['ids'] = obj_ids 
        return self._print_report(cr, uid, ids, data, context=context)

        name = fields.Char(string='Name')
        report = fields.Selection([('coop_register', 'Cooperators Register'),
                                     ('operation_register', 'Operations Register')],
                                    string='Report',
                                    required=True, default='coop_register')
        display_cooperator = fields.Selection([('all', 'All'),
                                             ('member', 'Effective member')],
                                            string='Display cooperator',
                                            required=True, default='all')
