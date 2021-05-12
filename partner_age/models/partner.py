# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    age = fields.Integer(string="Age", compute="_compute_age", search="_search_age")

    def _search_age(self, operator, value):
        if operator not in ("=", "!=", "<", "<=", ">", ">=", "in", "not in"):
            return []
        # pylint: disable=sql-injection
        # the value of operator is checked, no risk of injection
        query = """
            SELECT id
            FROM res_partner
            WHERE extract(year from age(CURRENT_DATE, birthdate_date))
              {operator} %s
            """.format(
            operator=operator
        )
        self.env.cr.execute(query, (value,))
        ids = [t[0] for t in self.env.cr.fetchall()]
        return [("id", "in", ids)]

    @api.multi
    @api.depends("birthdate_date")
    def _compute_age(self):
        for partner in self:
            if partner.birthdate_date:
                birthday = partner.birthdate_date
                today = datetime.now().date()
                partner.age = (
                    today.year
                    - birthday.year
                    - ((today.month, today.day) < (birthday.month, birthday.day))
                )
