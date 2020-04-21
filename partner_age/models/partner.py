from datetime import datetime

from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _search_age(self, operator, value):
        if operator not in ("=", "!=", "<", "<=", ">", ">=", "in", "not in"):
            return []
        query = """SELECT id
                   FROM "%s"
                   WHERE extract(year from age(CURRENT_DATE,
                                               birthdate_date)) %s %%s""" % (
            self._table,
            operator,
        )
        self.env.cr.execute(query, (value,))
        ids = [t[0] for t in self.env.cr.fetchall()]
        return [("id", "in", ids)]

    @api.multi
    @api.depends("birthdate_date")
    def _compute_age(self):
        self.ensure_one()
        if self.birthdate_date:
            dBday = datetime.strptime(
                str(self.birthdate_date), OE_DFORMAT
            ).date()
            dToday = datetime.now().date()
            self.age = (
                dToday.year
                - dBday.year
                - ((dToday.month, dToday.day) < (dBday.month, dBday.day))
            )

    age = fields.Integer(
        string="Age", compute="_compute_age", search="_search_age"
    )
