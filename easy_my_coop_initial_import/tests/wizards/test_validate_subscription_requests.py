from odoo.tests.common import SavepointCase


class TestValidateSubscriptionRequestsWizard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestValidateSubscriptionRequestsWizard, cls).setUpClass()

    def test_force_validate_all_in_draft(self):
        wizard = (
            self.env["validate.subscription.request.wizard"]
            .with_context(active_id=self.subscription_requests.id)
            .create({"force_validate_all_in_draft": True})
        )

        wizard.validate()

        queue_jobs_before = self.env["queue.job"].search([])
        line_create.create_payment_lines()
        queue_jobs_after = self.env["queue.job"].search([])
        self.assertEquals(3, len(queue_jobs_after) - len(queue_jobs_before))
