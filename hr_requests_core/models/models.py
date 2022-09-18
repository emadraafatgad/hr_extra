# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class letter_type(models.Model):
    _name = 'letter.type'

    name = fields.Char(string='Name')


class hr_promotion(models.Model):
    _name = 'hr.promotion'

    name = fields.Char(string='Reason')
    date = fields.Date("Date")
    amount = fields.Float("Amount")
    contract_id = fields.Many2one("hr.contract")


class hr_penalty(models.Model):
    _name = 'hr.penalty'

    name = fields.Char(string='Reason')
    date = fields.Date("Date")
    amount = fields.Float("Amount")
    contract_id = fields.Many2one("hr.contract")


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    old_salary = fields.Float(string='Old Salary')
    old_phoneallowance = fields.Float(string='Old Phone Allowance')
    old_otherallowances = fields.Float(string='Old Other Allowances')
    salary_from = fields.Date(string="Salary start date")
    penalty_ids = fields.One2many("hr.penalty", 'contract_id', string='Penalties', readonly=True)
    promotion_ids = fields.One2many("hr.promotion", 'contract_id', string='Promotions', readonly=True)
    request_ids = fields.One2many('hr.request', 'request_contract_id', string="Requests", readonly=True)


class trip_requirement(models.Model):
    _name = "trip.requirement"

    name = fields.Char("Name")


class hr_employee(models.Model):
    _inherit = 'hr.employee'


class hr_requests_new(models.Model):
    _name = 'hr.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', compute="_compute_name")
    date = fields.Date('Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Confirmed'),
        ('done', 'done'),
        ('cancel', 'Rejected'),
    ], string='Status', default='draft', track_visibility='onchange', )
    # ,default='draft', readonly=True, index = True, copy = False, track_visibility = 'onchange',
    type = fields.Selection([
        ('unrenew', 'Un Renew Contract عدم تجديد العقد'),
        ('resign', 'Resignation استقالة'),
        ('terminate', 'Termination إقاللة'),
        ('promote', 'Promotion ترقية'),
        ('trip', 'Business Trip رحلة عمل'),
        ('suspend', 'Stop Salary إيقاف الراتب'),
        ('unsuspend', 'Release Salary استرجاع الراتب'),
        ('letter', 'Letter خطاب'),
        ('penalty', 'Penalty عقوبة')
    ], string='Type', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env['hr.employee'].search(
        [('user_id', '=', self.env.uid)], limit=1))
    approver_ids = fields.Many2many('hr.employee', string='Pending Approver', readonly=True)
    request_contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)
    employee_id1 = fields.Many2one('hr.employee', string='Employee', domain="[('active','=', False)]")
    emp_id = fields.Char(string='Identification No', related='employee_id.identification_id', readonly=True)
    job_id = fields.Many2one('hr.job', 'Job Position', related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', related='employee_id.department_id', readonly=True)
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', related='employee_id.country_id', readonly=True)
    contract = fields.Many2one('hr.contract', compute='_compute_contract', readonly=True)
    date_start = fields.Date('Joining Date', related='contract.date_start', readonly=True)
    # houseallowance = fields.Float(string='House Allowance', related='contract.houseallowance', readonly=True)
    # transallowance = fields.Float(string='Transportation Allowance', related='contract.transallowance', readonly=True)
    phoneallowance = fields.Float(string='Phone Allowance', compute="_compute_contract", store=True)
    otherallowances = fields.Float(string='Other Allowances', compute="_compute_contract", store=True)
    wage = fields.Float('Wage', readonly=True, compute="_compute_contract")
    reason = fields.Text(required=True)
    last = fields.Date("Last Working Date")
    am_type = fields.Selection([
        ('fix', 'Fixed Amount'),
        ('percent', 'Percentage'),
    ], string='Amount Type', default='fix')
    pen_am_type = fields.Selection([
        ('fix', 'Fixed Amount'),
        ('percent', 'Percentage'),
        ('day', 'Days'),
    ], string='Penalty Amount Type', default='fix')
    pen_type = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('final', 'Final'),
    ], string='Penalty Type')
    amount = fields.Float("Amount")
    new_job_id = fields.Many2one('hr.job', 'New Job Position', default=lambda self: self.env['hr.employee'].search(
        [('id', '=', self.employee_id.id)], limit=1).job_id.id)
    new_phoneallowance = fields.Float(string='New Phone Allowance',
                                      default=lambda self: self.env['hr.contract'].search(
                                          [('id', '=', self.contract.id)], limit=1).phoneallowance)
    new_otherallowances = fields.Float(string='New Other Allowances',
                                       default=lambda self: self.env['hr.contract'].search(
                                           [('id', '=', self.contract.id)], limit=1).otherallowances)
    value = fields.Float('Total amount', compute='_compute_sheet')
    letter = fields.Char("Send Letter to")
    stamp = fields.Selection([
        ('sas', 'SAS'),
        ('chamber', 'Chamber'),
    ], string='Stamp From')
    dest_from = fields.Char("Destination From")
    dest_to = fields.Char("To")
    per_from = fields.Date("Period From")
    per_to = fields.Date("To")
    let_type = fields.Many2one('letter.type', string="Letter Type")
    apply_from = fields.Date("Apply From")
    visa = fields.Boolean("Visa")
    hotel = fields.Boolean("Residance hotel")
    ticket = fields.Boolean("Ticket")
    liv_pay = fields.Boolean("Living payment")
    transport = fields.Boolean("Transportation")

    # req_ids = fields.Many2many("trip.requirement", string="Trip Requirements")

    @api.constrains('employee_id')
    def check_employee(self):
        if not (self.employee_id.user_id.id == self.env.uid or self.employee_id.parent_id.user_id.id == self.env.uid
                or self.env.user.has_group('hr.group_hr_manager')):
            raise UserError('You can not create or edit Request related to this employee')

    @api.one
    @api.depends('employee_id', 'type', 'employee_id1')
    def _compute_name(self):
        if self.type == 'unsuspend':
            self.name = str(self.employee_id1.name) + ' ' + str(self.type) + ' Request'
        else:
            self.name = str(self.employee_id.name) + ' ' + str(self.type) + ' Request'

    @api.one
    @api.depends('amount', 'am_type', 'type', 'pen_am_type')
    def _compute_sheet(self):
        # if self.state != 'draft':
        if self.type == 'promote':
            if self.am_type == 'fix':
                self.value = self.amount
            else:
                self.value = self.amount * self.wage / 100

        if self.type == 'penalty':
            if self.pen_am_type == 'fix':
                self.value = self.amount
            elif self.pen_am_type == 'day':
                day_wage = self.wage / 30
                self.value = day_wage * self.amount
            else:
                self.value = self.amount * self.wage / 100

    @api.one
    @api.depends('employee_id')
    def _compute_contract(self):
        self.contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                        ('state', '=', 'open')], limit=1)
        if self.state == 'done':
            self.wage = self.env['hr.contract'].search([('id', '=', self.contract.id)], limit=1).old_salary
        else:
            self.wage = self.env['hr.contract'].search([('id', '=', self.contract.id)], limit=1).wage
        self.phoneallowance = self.env['hr.contract'].search([('id', '=', self.contract.id)], limit=1).phoneallowance
        self.otherallowances = self.env['hr.contract'].search([('id', '=', self.contract.id)], limit=1).otherallowances
        # phoneallowance = fields.Float(string='Phone Allowance', related='contract.phoneallowance', readonly=True)
        # otherallowances

    def action_approve(self):
        # body = self.name+"Approved"
        # self.employee_id.parent_id.user_id.notify_info(body)
        if self.employee_id.parent_id.user_id.id != self.env.uid and self.type != 'unsuspend':
            raise UserError('Only direct manager can approve this Request')
        if self.employee_id1.parent_id.user_id.id != self.env.uid and self.type == 'unsuspend':
            raise UserError('Only direct manager can approve this Request')
        if self.type == 'unrenew':
            x = 'Un Renew Contract'
        elif self.type == 'resign':
            x = 'Resignation'
        elif self.type == 'terminate':
            x = 'Termination'
        elif self.type == 'promote':
            x = 'Promotion'
        elif self.type == 'trip':
            x = 'Business Trip'
        elif self.type == 'suspend':
            x = 'Stop Salary'
        elif self.type == 'unsuspend':
            x = 'Release Salary'
        elif self.type == 'letter':
            x = 'Letter'
        else:
            x = 'Penalty'
        if self.date_start:
            joining = self.date_start
        else:
            joining = ''
        users = self.env['res.users'].search([])
        uids = []
        apps = []
        for u in users:
            if u.has_group('hr.group_hr_manager'):
                apps.append(u.id)
                uids.append(u.partner_id.id)
        approvers = self.env['hr.employee'].search([('user_id', 'in', apps)])
        app_ids = []
        for a in approvers:
            app_ids.append(a.id)
        return self.write({
            'state': 'approve',
            'approver_ids': [(6, 0, app_ids)]
        })

    @api.constrains('employee_id', 'employee_id1', 'type')
    def check_expr_date(self):
        for each in self:
            if (not (each.employee_id.parent_id.user_id.id == self.env.uid or
                     self.env.user.has_group('hr.group_hr_manager'))) and each.type in ['suspend', 'terminate',
                                                                                        'penalty', 'promote']:
                raise UserError('Only Direct Manager or HR Manager Can Create or edit this typ of request.')
            # elif each.employee_id.parent_id.id != self.env.uid and each.state == 'draft' and each.type in ['suspend', 'penalty']:
            #     each.write({'state': 'approve'})
            elif (not (each.employee_id1.parent_id.user_id.id == self.env.uid or
                       self.env.user.has_group('hr.group_hr_manager'))) and each.type == 'unsuspend':
                raise UserError('Only Direct Manager or HR Manager Can Create or edit this typ of request.')
            # elif each.employee_id1.parent_id.id != self.env.uid and each.state == 'draft' and each.type == 'unsuspend':
            #     each.write({'state': 'approve'})

    def action_done(self):
        if self.state == 'draft' and self.type != 'letter':
            raise UserError("Only Letter can be confirmed from Draft")
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                   ('state', '=', 'open')], limit=1)
        emp = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        emp1 = self.env['hr.employee'].search([('id', '=', self.employee_id1.id), ('active', '=', False)], limit=1)
        if self.type == 'unrenew':
            self.env['termination.termination'].create({
                'employee': self.employee_id.id,
                'name': 'unrenew',
                'end_of_service': self.apply_from
            })
        elif self.type == 'resign':
            self.env['termination.termination'].create({
                'employee': self.employee_id.id,
                'name': 'resignation',
                'end_of_service': self.apply_from
            })
        elif self.type == 'terminate':
            self.env['termination.termination'].create({
                'employee': self.employee_id.id,
                'name': 'termination',
                'end_of_service': self.apply_from
            })
        elif self.type == 'promote':
            wage = contract.wage
            phone = contract.phoneallowance
            contract.write({
                'old_salary': wage,
                'salary_from': self.apply_from,
                'wage': wage + self.value,
                'old_phoneallowance': phone,
                'phoneallowance': self.new_phoneallowance,
                'job_id': self.new_job_id.id
            })
            if self.new_phoneallowance:
                contract.write({
                    'old_phoneallowance': phone,
                    'phoneallowance': self.new_phoneallowance
                })
            if self.new_otherallowances:
                contract.write({
                    'old_otherallowances': phone,
                    'otherallowances': self.new_otherallowances
                })
            if self.new_job_id:
                emp.write({
                    'job_id': self.new_job_id.id
                })
            self.env['hr.promotion'].create({
                'name': self.reason,
                'date': self.apply_from,
                'amount': self.value,
                'contract_id': contract.id
            })
        # elif self.type == 'letter':
        elif self.type == 'suspend':
            emp.write({
                'active': False,
            })
        elif self.type == 'unsuspend':
            emp1.sudo().write({
                'active': True,
            })
        elif self.type == 'penalty':
            self.env['hr.penalty'].create({
                'name': self.reason,
                'date': self.apply_from,
                'amount': self.value,
                'contract_id': contract.id
            })

        if self.type == 'unrenew':
            x = 'Un Renew Contract'
        elif self.type == 'resign':
            x = 'Resignation'
        elif self.type == 'terminate':
            x = 'Termination'
        elif self.type == 'promote':
            x = 'Promotion'
        elif self.type == 'trip':
            x = 'Business Trip'
        elif self.type == 'suspend':
            x = 'Stop Salary'
        elif self.type == 'unsuspend':
            x = 'Release Salary'
        elif self.type == 'letter':
            x = 'Letter'
        else:
            x = 'Penalty'
        if self.date_start:
            joining = self.date_start
        else:
            joining = ''

        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                   ('state', '=', 'open')], limit=1)
        if contract:
            return self.write({
                'state': 'done',
                'request_contract_id': contract.id,
                'approver_ids': [(5)]
            })
        else:
            return self.write({
                'state': 'done',
                'approver_ids': [(5)]
            })

    @api.one
    def action_cancel(self):
        if (not (self.employee_id.parent_id.user_id.id == self.env.uid or self.env.user.has_group(
                'hr.group_hr_manager'))) and \
                self.type != 'unsuspend':
            raise UserError('Only direct manager and HR Manager can refuse this Request')
        if (not (self.employee_id1.parent_id.user_id.id == self.env.uid or self.env.user.has_group(
                'hr.group_hr_manager'))) and \
                self.type == 'unsuspend':
            raise UserError('Only direct manager and HR Manager can refuse this Request')
        emp = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        type = ''
        if self.type == 'unrenew':
            type = 'unrenew'
        elif self.type == 'terminate':
            type = 'termination'
        elif self.type == 'resign':
            type = 'resignation'
        if self.type == 'suspend':
            emp.write({
                'active': True,
            })
        elif self.type in ['unrenew', 'terminate', 'resign']:
            self.env['termination.termination'].search([('end_of_service', '=', self.apply_from),
                                                        ('employee', '=', self.employee_id.id),
                                                        ('name', '=', type)]).unlink()

        if self.type == 'unrenew':
            x = 'Un Renew Contract'
        elif self.type == 'resign':
            x = 'Resignation'
        elif self.type == 'terminate':
            x = 'Termination'
        elif self.type == 'promote':
            x = 'Promotion'
        elif self.type == 'trip':
            x = 'Business Trip'
        elif self.type == 'suspend':
            x = 'Stop Salary'
        elif self.type == 'unsuspend':
            x = 'Release Salary'
        elif self.type == 'letter':
            x = 'Letter'
        else:
            x = 'Penalty'
        if self.date_start:
            joining = self.date_start
        else:
            joining = ''
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                   ('state', '=', 'open')], limit=1)
        if contract:
            return self.write({
                'state': 'cancel',
                'request_contract_id': contract.id,
                'approver_ids': [(5)]
            })
        else:
            return self.write({
                'state': 'cancel',
                'approver_ids': [(5)]
            })

    def action_draft(self):
        return self.write({'state': 'draft'})
