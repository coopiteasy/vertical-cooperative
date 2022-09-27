# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # previously, when a subscription request was created from an existing
    # contact (as opposed to creating one without a contact, which would
    # create the contact when it would be validated), the subscription type
    # was set to "subscription" instead of the default value "new". this is
    # not a useful distinction, so it has been removed.
    cr.execute(
        """
        update subscription_request
        set type = 'new'
        where type = 'subscription'
        """
    )
