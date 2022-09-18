# -*- coding: utf-8 -*-

import math

import dateutil.parser
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    annual = fields.Boolean("Annual")


class hrHolidays(models.Model):
    _inherit = "hr.holidays"

    date_from = fields.Date('Start Date', readonly=True, index=True, copy=False,
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                            track_visibility='onchange')
    date_to = fields.Date('End Date', readonly=True, copy=False,
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                          track_visibility='onchange')
    add_ticket = fields.Boolean("Add Ticket")
    add_visa = fields.Boolean("Add Visa")
    tdate_from = fields.Date("Ticket date from")
    tdate_to = fields.Date("Ticket date to")
    tdest_from = fields.Char("Ticket Destination from")
    tdest_to = fields.Char("Ticket Destination to")
    vac_id = fields.Many2one('vacation.request', string="Vacation", readonly=True)
    vac_state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Confirmed'),
        ('cancel', 'Rejected')
    ], related="vac_id.state", readonly=True, string="Vacation Status")
    annual = fields.Boolean("Annual", related="holiday_status_id.annual", readonly=True)
    from_balance = fields.Boolean("From my Vacations")
    balance = fields.Float(string='Vacation balance(Days)', compute="_compute_balance", store=True)
    current_balance = fields.Float(string='Current vacation balance', compute="_compute_balance", store=True)
    advan = fields.Boolean("Advance Salary")

    @api.onchange('annual')
    def _onchange_annual(self):
        if self.annual is True:
            self.from_balance = True
        else:
            self.from_balance = False

    @api.depends('date_from', 'employee_id')
    def _compute_balance(self):
        for holiday in self:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', holiday.employee_id.id), ('state', '=', 'open')],
                limit=1)
            date_start = fields.Datetime.from_string(contract.date_start)
            date_end = fields.Datetime.from_string(holiday.date_from)
            difference_day = relativedelta(date_end, date_start)
            cur_date_end = fields.Datetime.from_string(holiday.create_date)
            cur_difference_day = relativedelta(cur_date_end, date_start)
            working_month = (12 * difference_day.years) + difference_day.months
            current_working_month = (12 * cur_difference_day.years) + cur_difference_day.months
            holiday.balance = (contract.annualvacation * working_month / 12) - contract.done_vac
            holiday.current_balance = (contract.annualvacation * current_working_month / 12) - contract.done_vac

    @api.constrains('number_of_days_temp', 'balance', 'annual')
    def check_balance(self):
        for holiday in self:
            if holiday.number_of_days_temp > holiday.balance and holiday.annual == True:
                raise UserError("Leave period Must be less than or equal Vacation balance")

    @api.multi
    def action_validate(self):
        self._check_security_action_validate()

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'second_approver_id': current_employee.id})
            else:
                holiday.write({'first_approver_id': current_employee.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                holiday._validate_leave_request()
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
            if holiday.holiday_status_id.annual and holiday.from_balance == False and holiday.type == 'remove':
                vac = self.env['vacation.request'].create({
                    'employee_id': holiday.employee_id.id,
                    'date_from': dateutil.parser.parse(holiday.date_from).date(),
                    'date_to': dateutil.parser.parse(holiday.date_to).date(),
                })
                holiday.write({
                    'vac_id': vac.id,
                })
            if holiday.from_balance and holiday.type == 'remove':
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
                contract.write({
                    'vac_balance': contract.vac_balance - self.number_of_days_temp,
                    'done_vac': contract.done_vac + self.number_of_days_temp
                })
        return True

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days) + 1


class hr_vacation(models.Model):
    _name = 'vacation.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    vacation_count = fields.Integer(compute='_compute_vacation_count', string='Land Costs')
    name = fields.Char(string="Name", default='Annual Vacation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Confirmed'),
        ('cancel', 'Rejected')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    active = fields.Boolean("Active", default=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_name = fields.Char(related='employee_id.name')
    employee_department = fields.Many2one(related='employee_id.department_id', readonly=True)
    date_from = fields.Date("vacation from", default=fields.Date.today)
    date_to = fields.Date("vacation to", default=fields.Date.today)
    vac_period = fields.Integer("period", compute="_compute_vacation", store=True, readonly=True)
    work_days = fields.Integer("Work Days", compute="_compute_vacation", store=True, readonly=True)
    remain = fields.Float(string='Vacation remaining days', compute="compute_sheet", store=True)
    balance = fields.Float(string='Vacation balance(Days)', compute="_compute_balance", store=True)
    payslips_ids = fields.One2many('hr.payslip', 'vacation_id')
    # account_control_ids = fields.Many2many('account.account', 'account_account_type_rel', 'journal_id', 'account_id',
    #                                        string='Accounts Allowed',
    #                                        domain=[('deprecated', '=', False)])
    vac_indemnity = fields.Float(string='Total Vacation Amount', compute="_compute_vacation", store=True, readonly=True)
    vac_salary = fields.Float(string='Advance salary', compute="_compute_vacation", store=True, readonly=True)
    net_salary = fields.Float("Salary", compute="_compute_salary")
    wags = fields.Float(string='‎Wags', compute="compute_sheet", readonly=True, store=True)
    cont_start_date = fields.Date(string="Start Date", compute="compute_sheet", readonly=True)
    cont_end_date = fields.Date(string="End Date", compute="compute_sheet", readonly=True)
    trans_allow = fields.Float('Transportation Allowance', compute="compute_sheet", readonly=True)
    phone_allow = fields.Float('Phone Allowance', compute="compute_sheet", readonly=True)
    other_allow = fields.Float('Other Allowances', compute="compute_sheet", readonly=True)
    houseallowan = fields.Float('House Allowance', compute="compute_sheet", readonly=True)
    bank_fees = fields.Float('Bank Fees', compute="compute_sheet", readonly=True)
    cont_hasvacationeach = fields.Float("Has Vacation Each", compute="compute_sheet", store=True)
    cont_annual_vacation = fields.Float("Annual Vacation Period", compute="compute_sheet", store=True)
    cont_has_ticket_each = fields.Float("Has Vacation Each", compute="compute_sheet", store=True)
    cont_no_tickets = fields.Float("No of Tickets", compute="compute_sheet", store=True)
    other_deductions = fields.Float('Other Deduction', compute="compute_sheet", readonly=True)
    vac_add = fields.Float("Other Additions")
    vac_ded = fields.Float("Other Deductions")
    last_vac = fields.Date("Last Vacation Date", compute="_compute_vacation")
    cont_ticket = fields.Integer("Remaining vacation ticket", compute="_compute_ticket", default=0)
    add_ticket = fields.Boolean("Add Tickets")
    ticket_no = fields.Integer("No. Of Tickets")
    ticket_amount = fields.Float("Ticket Amount")
    vac_amount = fields.Float("Vacation Amount", compute="_compute_amount", store=True)
    tot_tick = fields.Float("Ticket Amount", compute="_compute_tot")
    tot_ded = fields.Float("Deduction Amount", compute="_compute_tot")
    tot_add = fields.Float("Addition Amount", compute="_compute_tot")
    move_id = fields.Many2one('account.move', 'Journal Entry', copy=False)

    @api.multi
    def unlink(self):
        if any(vac.state == 'done' for vac in self):
            raise UserError(_('Cannot delete confirmed vacation request'))
        return super(hr_vacation, self).unlink()

    @api.one
    @api.depends('cont_start_date', 'date_from')
    def _compute_balance(self):
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'open')],
                                                  limit=1)
        date_start = fields.Datetime.from_string(self.cont_start_date)
        date_end = fields.Datetime.from_string(self.date_from)
        difference_day = relativedelta(date_end, date_start)
        working_month = (12 * difference_day.years) + difference_day.months
        self.balance = (contract.annualvacation * working_month / 12) - contract.done_vac

    @api.one
    @api.depends('vac_add', 'vac_ded', 'ticket_amount', 'ticket_no')
    def _compute_tot(self):
        self.tot_tick = self.ticket_amount * self.ticket_no
        self.tot_add = self.vac_add
        self.tot_ded = self.vac_ded

    @api.one
    @api.depends('wags', 'balance')
    def _compute_amount(self):
        self.vac_amount = (self.wags / 30) * self.balance

    @api.multi
    def _compute_vacation_count(self):
        for vac in self:
            vac.vacation_count = self.env['vacation.request'].search_count(
                [('employee_id', '=', vac.employee_id), ('state', '=', 'done')])

    def _compute_ticket(self):
        reqs = self.env['vacation.request'].search([('employee_id', '=', self.employee_id.id), ('active', '=', True),
                                                    ('state', '=', 'done')])
        tickets = 0
        if reqs:
            for r in reqs:
                tickets += r.ticket_no
            self.cont_ticket = self.cont_no_tickets - tickets
        else:
            self.cont_ticket = self.cont_no_tickets

    @api.one
    @api.depends('employee_id', 'cont_annual_vacation', 'cont_start_date', 'date_from', 'date_to', 'wags', 'vac_period',
                 'houseallowan', 'net_salary', 'vac_ded', 'vac_add', 'ticket_amount', 'ticket_no')
    def _compute_vacation(self):
        date_start = fields.Datetime.from_string(self.date_from)
        date_end = fields.Datetime.from_string(self.date_to)
        difference_day = relativedelta(date_end, date_start)
        self.vac_period = (365 * difference_day.years) + (30 * difference_day.months) + (difference_day.days)
        reqs = self.env['vacation.request'].search(
            [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'done')])
        days = 0
        x = self.id
        last = self.cont_start_date
        if reqs:
            for r in reqs:
                days += r.vac_period
                if r.id != x:
                    if r.date_to > last:
                        last = r.date_to
        self.last_vac = last

        self.last_vac = last

        dfrom = fields.Datetime.from_string(last)
        dto = fields.Datetime.from_string(self.date_from)
        difference_day = relativedelta(dto, dfrom)
        self.work_days = (365 * difference_day.years) + (30 * difference_day.months) + (difference_day.days)
        self.vac_indemnity = self.wags * self.balance / 30 + self.vac_add - self.vac_ded + self.net_salary + (
                self.ticket_amount * self.ticket_no)
        self.vac_salary = self.wags * self.balance / 30 + self.vac_add - self.vac_ded + \
                          (self.ticket_amount * self.ticket_no)

    @api.one
    def action_done(self):
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'open')],
                                                  limit=1)
        contract.write({
            'vac_balance': contract.vac_balance - self.balance,
            'done_vac': contract.done_vac + self.balance
        })
        accs = self.env['hr.accounts'].search([('company_id', '=', self.employee_id.company_id.id)], limit=1)
        if not accs or not accs.tickets_exp_acc or not accs.tickets_accrual_acc \
                or not accs.vacation_accrual_acc or not accs.vacation_exp_acc or not accs.vac_journal_id:
            raise ValidationError("Please enter HR Accounts for this employee company to complete Journal entry for "
                                  "this Vacation")
        company_currency = self.employee_id.company_id.currency_id.id
        vac_salary = self.wags * self.balance / 30 + self.vac_add - self.vac_ded
        move_line_2 = {
            'name': self.name,
            'account_id': accs.vacation_exp_acc.id,
            'debit': vac_salary,
            'credit': 0.0,
            'journal_id': accs.vac_journal_id.id,
            # 'partner_id': self.partner_id.id,
            # 'analytic_account_id': self.category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency or False,
            'amount_currency': company_currency and 1.0 * vac_salary or 0.0,
        }
        move_line_4 = {
            'name': self.name,
            'account_id': accs.vacation_accrual_acc.id,
            'debit': 0.0,
            'credit': vac_salary,
            'journal_id': accs.vac_journal_id.id,
            # 'partner_id': self.partner_id.id,
            # 'analytic_account_id': self.category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency or False,
            'amount_currency': company_currency and - 1.0 * self.ticket_amount or 0.0,
        }
        lines = [(0, 0, move_line_2), (0, 0, move_line_4)]
        if self.ticket_amount * self.ticket_no:
            move_line_3 = {
                'name': self.name,
                'account_id': accs.tickets_accrual_acc.id,
                'debit': 0.0,
                'credit': self.ticket_amount * self.ticket_no,
                'journal_id': accs.vac_journal_id.id,
                # 'partner_id': self.partner_id.id,
                # 'analytic_account_id': self.category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency or False,
                'amount_currency': company_currency and - 1.0 * self.ticket_amount or 0.0,
            }
            move_line_1 = {
                'name': self.name,
                'account_id': accs.tickets_exp_acc.id,
                'debit': self.ticket_amount * self.ticket_no,
                'credit': 0.0,
                'journal_id': accs.vac_journal_id.id,
                # 'partner_id': self.partner_id.id,
                'currency_id': company_currency or False,
                'amount_currency': company_currency and 1.0 * self.ticket_amount or 0.0,
            }
            lines.append((0, 0, move_line_1))
            lines.append((0, 0, move_line_3))

        move_vals = {
            'name': self.name,
            'ref': self.name,
            'date': self.date_from or False,
            'journal_id': accs.vac_journal_id.id,
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

    @api.depends("employee_id")
    def compute_sheet(self):
        for e in self:
            e.wags = self.env['hr.contract'].search([('employee_id', '=', e.employee_id.id), ('state', '=', 'open')],
                                                    limit=1).wage
            e.cont_start_date = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).date_start
            e.cont_end_date = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).date_end
            e.trans_allow = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).transallowance
            e.phone_allow = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).phoneallowance
            e.other_allow = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).otherallowances
            e.houseallowan = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).houseallowance
            e.bank_fees = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).bankfees
            e.other_deductions = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).otherdeducions
            e.cont_hasvacationeach = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).hasvacationeach
            e.cont_annual_vacation = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).annualvacation
            e.cont_has_ticket_each = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).hasticketseach
            e.cont_no_tickets = self.env['hr.contract'].search(
                [('employee_id', '=', e.employee_id.id), ('state', '=', 'open')], limit=1).no_tickets
            e.remain = self.env['hr.contract'].search([('employee_id', '=', e.employee_id.id), ('state', '=', 'open')],
                                                      limit=1).vac_balance


class hr_payroll(models.Model):
    _inherit = 'hr.payslip'
    vacation_id = fields.Many2one('vacation.request')
