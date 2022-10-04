# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # recompute subscription request names for companies, as they were
    # incorrectly computed.
    cr.execute(
        """
        update subscription_request
        set name = company_name
        where is_company
        """
    )
