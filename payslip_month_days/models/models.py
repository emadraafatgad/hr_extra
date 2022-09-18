# -*- coding: utf-8 -*-

from odoo import models, fields, api


class payslip_month_days(models.Model):
    _inherit = 'hr.payslip'

    month_days = fields.Float(compute="_compute_month_days", store=True, string="Month Days")
    basic_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Basic Salary")
    house_salary = fields.Float(compute="_compute_basic_salary", store=True, string="House Allowance")
    trans_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Transportation Allowance")
    phone_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Phone Allowance")
    food_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Food  Allowance")
    over_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Over Time")
    other_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Other  Allownace")
    gosi_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Employee Gosi")
    bank_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Bank Fees")
    absence_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Absence")
    latency_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Latency")
    loan_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Loans")
    other_ded_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Other Deductions")
    gross_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Gross Salary")
    net_salary = fields.Float(compute="_compute_basic_salary", store=True, string="Net Salary")

    @api.depends('date_from')
    def _compute_month_days(self):
        for payslip in self:
            date = fields.Datetime.from_string(payslip.date_from)
            if date.month in [1, 3, 5, 7, 8, 10, 12]:
                payslip.month_days = 31
            elif date.month == 2:
                payslip.month_days = 28
            else:
                payslip.month_days = 30

    @api.depends('line_ids')
    def _compute_basic_salary(self):
        for record in self:
            for line in record.line_ids:
                if line.salary_rule_id.code == "BASIC":
                    record.basic_salary = line.total
                if line.salary_rule_id.code == "HOUSE":
                    record.house_salary = line.total
                if line.salary_rule_id.code == "TRANS":
                    record.trans_salary = line.total

                if line.salary_rule_id.code == "PHONE":
                    record.phone_salary = line.total

                if line.salary_rule_id.code == "FOOD":
                    record.food_salary = line.total

                if line.salary_rule_id.code == "Over":
                    record.over_salary = line.total
                if line.salary_rule_id.code == "OTHER":
                    record.other_salary = line.total
                if line.salary_rule_id.code == "EM GOSI":
                    record.gosi_salary = line.total
                if line.salary_rule_id.code == "BANK FEES":
                    record.bank_salary = line.total
                if line.salary_rule_id.code == "Abs":
                    record.absence_salary = line.total
                if line.salary_rule_id.code == "Late ":
                    record.latency_salary = line.total
                if line.salary_rule_id.code == "LO":
                    record.loan_salary = line.total
                if line.salary_rule_id.code == "other ded":
                    record.other_ded_salary = line.total
                if line.salary_rule_id.code == "GROSS":
                    record.gross_salary = line.total
                if line.salary_rule_id.code == "NET":
                    record.net_salary = line.total
