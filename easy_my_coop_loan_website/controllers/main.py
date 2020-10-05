from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class WebsiteLoanIssueSubscription(http.Controller):
    @http.route(
        ["/subscription/get_loan_issue"],
        type="json",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def get_loan_issue(self, loan_issue_id, **kw):
        loan_issue_obj = request.env["loan.issue"]
        partner = request.env.user.partner_id
        if loan_issue_id:
            loan_issue = loan_issue_obj.sudo().browse(int(loan_issue_id))
            max_amount = loan_issue.get_max_amount(partner)
            return {
                loan_issue.id: {
                    "max_amount": max_amount,
                    "face_value": loan_issue.face_value,
                }
            }
        else:
            return False

    def missing_mandatory_info(self):
        partner = request.env.user.partner_id
        if (
            not partner.bank_ids
            or not partner.birthdate_date
            or not partner.street
            or not partner.city
            or not partner.zip
            or not partner.country_id
            or not partner.gender
            or not partner.phone
        ):
            return False
        if partner.is_company:
            if (
                not partner.company_name
                or not partner.vat
            ):
                return False
        return True

    @http.route(
        ["/subscription/loan_issue_form"],
        type="http",
        auth="user",
        website=True,
    )
    def display_loan_issue_subscription_page(self, **kwargs):
        values = {}
        if not self.missing_mandatory_info():
            return request.redirect("/my/account")
        is_company = request.env.user.partner_id.is_company

        values = self.fill_values(values, is_company)
        values.update(kwargs=kwargs.items())
        return request.render(
            "easy_my_coop_loan_website.loanissuesubscription", values
        )

    def get_loan_issues(self, is_company):
        loan_obj = request.env["loan.issue"]
        loan_issues = loan_obj.sudo().get_web_issues(is_company)

        return loan_issues

    def fill_values(self, values, is_company):
        company = request.website.company_id
        loan_issues = self.get_loan_issues(is_company)

        values["loan_issues"] = loan_issues
        values["company"] = company

        if not values.get("loan_issue_id"):
            for loan_issue in loan_issues:
                if loan_issue.default_issue is True:
                    values["loan_issue_id"] = loan_issue.id
                    break
            if not values.get("loan_issue_id", False) and loan_issues:
                values["loan_issue_id"] = loan_issues[0].id

        return values

    def validation(self, loan_issue, kwargs):
        sub_amount = kwargs.get("subscription_amount")
        redirect = "easy_my_coop_loan_website.loanissuesubscription"

        values = {}
        if not loan_issue:
            values["error_msg"] = _("The selected loan issue is not found")
            return request.render(redirect, values)
        if sub_amount:
            values["error_msg"] = _("The amount shoud be of monetary type")
            return request.render(redirect, values)
        return True

    @http.route(
        ["/subscription/subscribe_loan_issue"],
        type="http",
        auth="user",
        website=True,
    )
    def loan_issue_subscription(self, **kwargs):
        loan_obj = request.env["loan.issue"]
        loan_obj_line = request.env["loan.issue.line"]

        loan_issue = loan_obj.sudo().browse(kwargs.get("loan_issue_id"))
        partner = request.env.user.partner_id

        if self.validation(loan_issue, kwargs):
            values = {
                "loan_issue_id": loan_issue.id,
                "partner_id": partner.id,
                "amount": kwargs["subscription_amount"],
                "state": "subscribed",
            }
            loan_obj_line.sudo().create(values)
        return request.render("easy_my_coop_website.cooperator_thanks", values)
