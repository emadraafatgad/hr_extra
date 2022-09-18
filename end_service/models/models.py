# -*- coding: utf-8 -*-

import calendar
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError, UserError


class end_service(models.Model):
    _name = 'termination.termination'

    name = fields.Selection(
        [('termination', 'Termination'), ('resignation', 'Resignation'), ('unrenew', 'Un Renew Contract')],
        string="Name", default='termination')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    employee = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_name = fields.Char(related='employee.name')
    employee_department = fields.Many2one(related='employee.department_id', readonly=True)
    end_of_service = fields.Date("End Of Service Date", default=fields.Date.today)
    work_years = fields.Float(string='Years of Work in Days', compute="_compute_amount", readonly=True)
    work_days = fields.Float(string='Years of Work', readonly=True, compute="_compute_amount")
    leaves_ids = fields.Float(string='Remainig off days', related='employee.remaining_leaves', readonly=True)
    payslips_ids = fields.One2many('hr.payslip', 'termination_id')
    leaving_indemnity = fields.Float(string='‎EOS amount', compute="_compute_amount", readonly=True)
    total_amount = fields.Float(string='Total amount', compute="_compute_amount", readonly=True)
    net_salary = fields.Float("Salary", compute="_compute_salary")
    wags = fields.Float(string='‎Wags', compute="_compute_amount", readonly=True)
    cont_start_date = fields.Date(string="Start Date", compute="_compute_amount", readonly=True)
    cont_end_date = fields.Date(string="End Date", compute="_compute_amount", readonly=True)
    trans_allow = fields.Float('Transportation Allowance', compute="_compute_amount", readonly=True)
    phone_allow = fields.Float('Phone Allowance', compute="_compute_amount", readonly=True)
    other_allow = fields.Float('Other Allowances', compute="_compute_amount", readonly=True)
    houseallowan = fields.Float('House Allowance', compute="_compute_amount", readonly=True)
    bank_fees = fields.Float('Bank Fees', compute="_compute_amount", readonly=True)
    other_deductions = fields.Float('Other Deduction', compute="_compute_amount", readonly=True)
    eos_add = fields.Float("Other Additions")
    eos_ded = fields.Float("Other Deductions")
    move_id = fields.Many2one('account.move', 'Journal Entry', copy=False)

    _sql_constraints = [
        ('unique_employee', 'UNIQUE(employee,state)',
         "A Employee already have End service record in same state. Employee must be unique!"),
    ]

    @api.multi
    def unlink(self):
        if any(production.state == 'done' for production in self):
            raise UserError(_('Cannot delete any confirmed end of service'))
        return super(end_service, self).unlink()

    def action_done(self):
        accs = self.env['hr.accounts'].search([('company_id', '=', self.employee.company_id.id)], limit=1)
        if not accs or not accs.end_of_service_accrual_acc or not accs.end_of_service_exp_acc or not accs.eos_journal_id:
            raise ValidationError("Please enter HR Accounts for this employee company to complete Journal entry for "
                                  "this EOS")
        company_currency = self.employee.company_id.currency_id.id
        move_line_1 = {
            'name': str(self.employee.name) + ' ' + str(self.name),
            'account_id': accs.end_of_service_exp_acc.id,
            'debit': self.leaving_indemnity + self.eos_add - self.eos_ded,
            'credit': 0.0,
            'journal_id': accs.eos_journal_id.id,
            # 'partner_id': self.partner_id.id,
            # 'analytic_account_id': self.category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency or False,
            'amount_currency': company_currency and 1.0 * self.leaving_indemnity or 0.0,
        }
        move_line_2 = {
            'name': str(self.employee.name) + ' ' + str(self.name),
            'account_id': accs.end_of_service_accrual_acc.id,
            'debit': 0.0,
            'credit': self.leaving_indemnity + self.eos_add - self.eos_ded,
            'journal_id': accs.eos_journal_id.id,
            # 'partner_id': self.partner_id.id,
            # 'analytic_account_id': self.category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency or False,
            'amount_currency': company_currency and - 1.0 * self.leaving_indemnity or 0.0,
        }
        lines = [(0, 0, move_line_1), (0, 0, move_line_2)]

        move_vals = {
            'name': str(self.employee.name) + ' ' + str(self.name),
            'ref': str(self.employee.name) + ' ' + str(self.name),
            'date': self.end_of_service or False,
            'journal_id': accs.eos_journal_id.id,
            'line_ids': lines,
        }
        move = self.env['account.move'].create(move_vals)
        move.post()
        return self.write({'state': 'done', 'move_id': move.id})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.depends("payslips_ids")
    def _compute_salary(self):
        salary = 0
        for rec in self:
            for p in rec.payslips_ids:
                for r in p.line_ids:
                    if r.code == 'NET':
                        salary += r.total
            rec.net_salary = salary


    @api.depends("employee", "name", "eos_add", "eos_ded", "net_salary","end_of_service")
    def _compute_amount(self):
        for e in self:
            e.wags = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                     ('state', '=', 'open')], limit=1).wage
            e.cont_start_date = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                                ('state', '=', 'open')], limit=1).date_start
            e.cont_end_date = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                              ('state', '=', 'open')], limit=1).date_end
            e.trans_allow = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                            ('state', '=', 'open')], limit=1).transallowance
            e.phone_allow = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                            ('state', '=', 'open')], limit=1).phoneallowance
            e.other_allow = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                            ('state', '=', 'open')], limit=1).otherallowances
            e.houseallowan = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                             ('state', '=', 'open')], limit=1).houseallowance
            e.bank_fees = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                          ('state', '=', 'open')], limit=1).bankfees
            e.other_deductions = self.env['hr.contract'].search([('employee_id', '=', e.employee.id),
                                                                 ('state', '=', 'open')], limit=1).otherdeducions
            leaves_to_cash = (e.wags / 30) * e.leaves_ids
            start_date = self.env['hr.contract'].search([('employee_id.id', '=', e.employee.id)]).date_start
            date_start = fields.Datetime.from_string(start_date)
            date_end = fields.Datetime.from_string(e.end_of_service)
            difference_day = relativedelta(date_end, date_start)
            e.work_years = (365 * difference_day.years) + (30 * difference_day.months) + (difference_day.days)
            e.work_days = difference_day.years

            if e.name == "termination":
                if 1.0 < (e.work_years / 365) <= 5.0:
                    e.leaving_indemnity = (((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                            - (e.bank_fees + e.other_deductions)) / 2.0) * (e.work_years / 365) 
                elif (e.work_years / 365) > 5.0:
                    remain = ((e.work_years / 365) - 5.0)
                    e.leaving_indemnity = ((((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                             - (e.bank_fees + e.other_deductions)) / 2.0) * 5.0) \
                                          + (remain * ((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                                       - (e.bank_fees + e.other_deductions))) 
                else:
                    e.leaving_indemnity = 0.0
            if e.name == "resignation":
                if 2.0 < (e.work_years / 365) <= 5.0:
                    e.leaving_indemnity = (((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                            - (e.bank_fees + e.other_deductions)) / 2.0) * (1 / 3) * (e.work_years / 365) 
                elif 10.0 >= (e.work_years / 365) > 5.0:
                    remain = ((e.work_years / 365) - 5.0)
                    e.leaving_indemnity = ((((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                             - (e.bank_fees + e.other_deductions)) / 2.0) * (1 / 3) * 5) \
                                          + ((((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                               - (e.bank_fees + e.other_deductions)) / 2.0) * (2 / 3) * remain)
                elif (e.work_years / 365) > 10.0:
                    remain = ((e.work_years / 365) - 10.0)
                    e.leaving_indemnity = ((((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                             - (e.bank_fees + e.other_deductions)) / 2.0) * (1 / 3) * 5) \
                                          + ((((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                               - (e.bank_fees + e.other_deductions)) / 2.0) * (2 / 3) * 5) + \
                                          ((((e.wags + e.houseallowan + e.trans_allow + e.phone_allow + e.other_allow + leaves_to_cash)
                                             - (e.bank_fees + e.other_deductions)) / 2.0) * remain) 
                else:
                    e.leaving_indemnity = 0.0

            e.total_amount = e.leaving_indemnity + e.eos_add - e.eos_ded + e.net_salary


class hr_pay(models.Model):
    _inherit = 'hr.payslip'
    period = fields.Integer(string="period", compute="_compute_period")
    termination_id = fields.Many2one('termination.termination')

    @api.one
    def _compute_period(self):
        date_start = fields.Datetime.from_string(self.date_from)
        date_end = fields.Datetime.from_string(self.date_to)
        period = relativedelta(date_end, date_start)
        self.period = period.days + (365 * period.years) + (30 * period.months)
