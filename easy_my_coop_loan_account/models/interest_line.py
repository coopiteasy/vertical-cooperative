# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LoanInterestLine(models.Model):
    _inherit = "loan.interest.line"

    loan_due_fy_move = fields.Many2one(
        comodel_name="account.move", string="Loan due this fiscal year account move"
    )
    loan_due_move = fields.Many2one(
        comodel_name="account.move", string="Loan due now account move"
    )
    loan_reimbursment_move = fields.Many2one(
        comodel_name="account.move", string="Loan reimbursement account move"
    )
    interest_closing_fy = fields.Many2one(
        comodel_name="account.move", string="Interest closing fiscal year account move"
    )
    interest_opening_fy = fields.Many2one(
        comodel_name="account.move", string="Interest opening fiscal year account move"
    )

    @api.multi
    def get_move_line(self, move_id, partner=None):
        self.ensure_one()
        move_line = {
            "date_maturity": self.due_date,
            "date": self.due_date,
            "move_id": move_id.id,
        }
        if partner:
            move_line["partner_id"] = partner.id
        return move_line

    @api.multi
    def create_move(self, date=None):
        self.ensure_one()
        if date:
            due_date = date
        else:
            due_date = self.due_date
        if not self.company_id.loan_journal:
            raise ValidationError(_("You must set Loan Journal on company"))

        return self.env["account.move"].create(
            {
                "ref": self.name,
                "date": due_date,
                "journal_id": self.company_id.loan_journal.id,
            }
        )

    @api.multi
    def generate_payment_move_lines(self):

        for line in self:
            if not self.loan_reimbursment_move:
                company = line.company_id
                move = line.create_move()

                debit_vals = line.get_move_line(move)
                loaner_vals = line.get_move_line(move, line.partner_id)

                debit_vals["debit"] = line.interest
                debit_vals["account_id"] = company.interest_account.id

                loan_vals = line.get_move_line(move)
                if line.due_loan_amount > 0:
                    loan_vals["debit"] = line.due_loan_amount
                    loan_vals["account_id"] = company.debt_long_term_due_account.id

                if line.due_loan_amount > 0 and line.net_interest > 0:
                    loaner_vals["credit"] = line.due_amount
                elif line.due_loan_amount > 0:
                    loaner_vals["credit"] = line.due_loan_amount
                elif line.net_interest > 0:
                    loaner_vals["credit"] = line.net_interest
                loaner_vals["account_id"] = company.loaner_account.id

                vals_list = [debit_vals, loan_vals, loaner_vals]

                if line.taxes_amount > 0:
                    tax_vals = line.get_move_line(move)
                    tax_vals["credit"] = line.taxes_amount
                    tax_vals["account_id"] = company.tax_account.id
                    vals_list.append(tax_vals)

                self.env["account.move.line"].create(vals_list)

                line.write({"loan_reimbursment_move": move.id, "state": "scheduled"})

    @api.multi
    def generate_interest_move_lines_fy(self, date, next_fy):
        """this function create the end of year accounting account for
        the accrued interest due for the closing fiscal year.
        """
        aml_obj = self.env["account.move.line"]
        for line in self:
            if not line.interest_closing_fy:
                company = line.company_id

                # compute the prorata interest for the fiscal year
                prorata_date = line.due_date - relativedelta(years=1)
                diff_days = (date - prorata_date).days
                days = line.issue_line.get_number_of_days(date.year)

                previous_interest = line.accrued_interest - line.interest
                prorata_interest = line.interest * (diff_days / days)
                interest_fy = previous_interest + prorata_interest

                # create interest closing account move lines
                close_fy_move = line.create_move(date)
                deb_vals = line.get_move_line(close_fy_move, line.partner_id)
                cred_vals = line.get_move_line(close_fy_move, line.partner_id)

                deb_vals["debit"] = interest_fy
                deb_vals["date"] = date
                deb_vals["account_id"] = company.interest_account.id

                cred_vals["credit"] = interest_fy
                cred_vals["date"] = date
                cred_vals["account_id"] = company.expense_account.id

                aml_obj.create([deb_vals, cred_vals])

                line.write({"interest_closing_fy": close_fy_move.id})

                # create interest opening account move lines
                opening_date = next_fy.date_from
                open_fy_move = line.create_move(opening_date)
                deb_vals = line.get_move_line(open_fy_move, line.partner_id)
                cred_vals = line.get_move_line(open_fy_move, line.partner_id)

                deb_vals["debit"] = interest_fy
                deb_vals["date"] = opening_date
                deb_vals["account_id"] = company.expense_account.id

                cred_vals["credit"] = interest_fy
                cred_vals["date"] = opening_date
                cred_vals["account_id"] = company.interest_account.id

                aml_obj.create([deb_vals, cred_vals])
                line.write({"interest_opening_fy": open_fy_move.id})

    @api.multi
    def generate_loan_due_fy(self, date):

        for line in self:
            if not line.loan_due_fy_move:
                company = line.company_id
                move = line.create_move(date)

                deb_vals = line.get_move_line(move, line.partner_id)
                cred_vals = line.get_move_line(move, line.partner_id)

                deb_vals["debit"] = line.due_loan_amount
                deb_vals["date"] = date
                deb_vals["account_id"] = company.debt_long_term_account.id

                cred_vals["credit"] = line.due_loan_amount
                cred_vals["date"] = date
                cred_vals["account_id"] = company.debt_long_term_fy_account.id

                self.env["account.move.line"].create([deb_vals, cred_vals])

                line.write({"loan_due_fy_move": move.id})

    @api.multi
    def generate_loan_due_now(self):
        """This function will generate the account move lines
        to transfer the due amount from long term debt account
        to the long term debt due (for this fiscal year) account
        """

        for line in self:
            if not line.loan_due_move:
                company = line.company_id
                move = line.create_move(line.due_date)

                debit_vals = line.get_move_line(move, line.partner_id)
                cred_vals = line.get_move_line(move, line.partner_id)

                debit_vals["debit"] = line.due_loan_amount
                debit_vals["account_id"] = company.debt_long_term_fy_account.id

                cred_vals["credit"] = line.due_loan_amount
                cred_vals["account_id"] = company.debt_long_term_due_account.id

                self.env["account.move.line"].create([debit_vals, cred_vals])

                line.write({"loan_due_move": move.id, "state": "due"})

    @api.model
    def _generate_payment_move(self):
        # TODO configure how many days before you want generate the move lines
        fy = self.env["account.fiscal.year"].get_next_fiscal_year()
        interest_lines = self.search(
            [
                ("due_date", ">=", fy.date_from),
                ("due_date", "<=", fy.date_to),
                ("due_amount", ">", 0),
                ("state", "=", "due"),
            ]
        )

        interest_lines.generate_payment_move_lines()

        return True

    @api.multi
    def action_paid(self):
        paid_by = self.env.context.get("paid_by_bank_statement")
        if paid_by:
            super(LoanInterestLine, self).action_paid()
        else:
            raise UserError(_("The payment must be registered" " by bank statement"))
