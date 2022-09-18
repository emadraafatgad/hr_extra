# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class exemption(models.Model):
    _name = 'exemption.exemption'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('hr.employee', string='Employee', required="True",
                           default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)],
                                                                               limit=1))
    late_hours = fields.Float('Permission Hours', required=True)
    late_reason = fields.Text("Reason Memo", required="True")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'confirmed'),
        ('done', 'Approved'),
        ('cancel', 'Rejected'),
    ], string='Status', default='draft', track_visibility='onchange')
    emp_id = fields.Char(string='Identification No', related='name.identification_id', readonly=True)
    type = fields.Selection([
        ('late', 'Late Sign in'),
        ('earl', 'Early Sign out'),
        ('other', 'Other'),
    ], string='Permission Type', required=True)
    date_from = fields.Float("From")
    date_to = fields.Float("To")
    date = fields.Date("Date", required=True)
    approver_ids = fields.Many2many('hr.employee', string='Pending Approver', readonly=True)
    reason_type = fields.Selection([
        ('personal', 'Personal'),
        ('work', 'Work'),
    ], string='Reason Type', required=True)
    exemption_contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)

    @api.onchange('date_from')
    def onChangeDate(self):
        if self.date_to:
            self.late_hours = self.date_to - self.date_from

    @api.onchange('date_to')
    def onChangeDateTo(self):
        if self.date_from:
            self.late_hours = self.date_to - self.date_from

    @api.constrains('name')
    def check_employee(self):
        if not (self.name.user_id.id == self.env.uid or self.name.parent_id.user_id.id == self.env.uid
                or self.env.user.has_group('hr.group_hr_manager') or self.env.user.has_group(
                    'hr_holidays.group_hr_holidays_user')):
            raise UserError('You can not create or edit Request related to this employee')

    def action_done(self):
        contract = self.env['hr.contract'].search([('employee_id', '=', self.name.id),
                                                   ('state', '=', 'open')], limit=1)
        if contract:
            return self.write({
                'state': 'done',
                'exemption_contract_id': contract.id,
                'approver_ids': [(5)]
            })
        else:
            return self.write({'state': 'done',
                               'approver_ids': [(5)]})

    def action_approve(self):
        if self.name.parent_id.user_id.id != self.env.uid:
            raise UserError('Only direct manager can approve this Request')
        users = self.env['res.users'].search([])
        uids = []
        apps = []
        for u in users:
            if u.has_group('hr_requests_core.group_hr_manager'):
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
        # return self.write({'state': 'approve'})

    def action_cancel(self):
        if (not (self.name.parent_id.user_id.id == self.env.uid or self.env.user.has_group('hr.group_hr_manager'))) and \
                self.state == 'draft':
            raise UserError('Only direct manager and HR Manager can refuse this Request')
        contract = self.env['hr.contract'].search([('employee_id', '=', self.name.id),
                                                   ('state', '=', 'open')], limit=1)
        if contract:
            return self.write({
                'state': 'cancel',
                'exemption_contract_id': contract.id,
                'approver_ids': [(5)]
            })
        else:
            return self.write({'state': 'cancel',
                               'approver_ids': [(5)]
                               })

    def action_draft(self):
        return self.write({'state': 'draft'})


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    exemption_ids = fields.One2many('exemption.exemption', 'exemption_contract_id', string="Permission Requests",
                                    readonly=True)
