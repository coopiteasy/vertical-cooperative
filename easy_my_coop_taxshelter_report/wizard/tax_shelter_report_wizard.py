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

class TaxShelterReport(models.TransientModel):
    _name = 'tax.shelter.report'
    
    name = fields.Char(string='Name')
    year = fields.Integer(string='Year', help='Introduce the year for which you want to get the report')
       
    def _print_report(self, data):
        return {'type': 'ir.actions.report.xml',
                'report_name': data['report'],
                'datas': data}
    
    @api.one
    def print_report(self):
        data = {}

        domain = [('cooperator','=','True'),('member','=','True')]
        coop = self.env['res.partner'].search(domain, order='cooperator_register_number')    
            
        data['model'] = 'res.partner'
        data['report'] = 'easy_my_coop_taxshelter_report.taxshelter_report' 
        data['ids'] = coop.ids 
        
        #return self._print_report(data)
        return self.env['report'].get_action(coop, 'easy_my_coop_taxshelter_report.tax_shelter_report')

        
