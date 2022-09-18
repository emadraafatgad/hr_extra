# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_requests(models.Model):
    _name = 'hr.request'

    name = fields.Char(string='Name', compute="_compute_name")
    date = fields.Date('Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    type = fields.Selection([
        ('renew', 'Renew Contract'),
        ('resign', 'Resignation'),
        ('terminate', 'Termination'),
        ('promote', 'Promotion'),
        ('trip', 'Business Trip'),
        ('suspend', 'Suspend Payroll'),
        ('letter', 'Letter'),
        ('penalty', 'Penalty')
    ], string='Type', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env['hr.employee'].search(
        [('user_id', '=', self.env.uid)], limit=1), required=True)
    emp_id = fields.Char(string='Identification No', related='employee_id.identification_id', readonly=True)
    job_id = fields.Many2one('hr.job', 'Job Position', related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', related='employee_id.department_id', readonly=True)
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', related='employee_id.country_id', readonly=True)
    contract = fields.Many2one('hr.contract', compute='_compute_contract', readonly=True)
    date_start = fields.Date('Joining Date', related='contract.date_start', readonly=True)
    # houseallowance = fields.Float(string='House Allowance', related='contract.houseallowance', readonly=True)
    # transallowance = fields.Float(string='Transportation Allowance', related='contract.transallowance', readonly=True)
    phoneallowance = fields.Float(string='Phone Allowance', related='contract.phoneallowance', readonly=True)
    otherallowances = fields.Float(string='Other Allowances', related='contract.otherallowances', readonly=True)
    wage = fields.Float('Wage', readonly=True, compute="_compute_contract")
    reason = fields.Text(required=True)
    last = fields.Date("Last Working Date")
    am_type = fields.Selection([
        ('fix', 'Fixed Amount'),
        ('percent', 'Percentage'),
    ], string='Amount Type', default='fix')
    pen_type = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('final', 'Final'),
    ], string='Penalty Type')
    amount = fields.Float("Amount")
    new_job_id = fields.Many2one('hr.job', 'New Job Position', default=lambda self: self.env['hr.employee'].search(
        [('id', '=', self.employee_id.id)], limit=1).job_id)
    new_phoneallowance = fields.Float(string='Phone Allowance', related='contract.phoneallowance',
                                      default=lambda self: self.env['hr.contract'].search(
                                          [('id', '=', self.contract.id)], limit=1).phoneallowance)
    new_otherallowances = fields.Float(string='Other Allowances', related='contract.otherallowances',
                                       default=lambda self: self.env['hr.contract'].search(
                                           [('id', '=', self.contract.id)], limit=1).otherallowances)
    new_wage = fields.Float('Wage', default=lambda self: self.wage)
    letter = fields.Char("Send Letter to")
    dest_from = fields.Char("Destination From")
    dest_to = fields.Char("To")
    per_from = fields.Char("Period From")
    per_to = fields.Char("To")

    @api.one
    @api.depends('employee_id', 'type')
    def _compute_name(self):
        self.name = str(self.employee_id.name) + ' ' + str(self.type) + ' Request'

    @api.one
    @api.depends('employee_id')
    def _compute_contract(self):
        self.contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                        ('state', '=', 'open')], limit=1)
        self.wage = self.env['hr.contract'].search([('id', '=', self.contract.id)], limit=1).wage

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_done(self):
        return self.write({'state': 'done'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_draft(self):
        return self.write({'state': 'draft'})
