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
        ('sent', 'Sent'),
        ('approve', 'Approved by Level 1'),
        ('majid', 'Approved by Level 2'),
        ('done', 'Approved'),
        ('cancel', 'Rejected'),
    ], string='Status', default='draft', readonly=True,
        index=True, copy=False, track_visibility='onchange')
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

    @api.onchange('employee_id')
    def _change_state(self):
        if self.employee_id.parent_id.user_id.id == self.env.uid:
            # self.write({'state': 'sent'})
            self.state = 'sent'
        else:
            self.state = 'draft'

    @api.onchange('employee_id1')
    def _change_state1(self):
        if self.employee_id1.parent_id.user_id.id == self.env.uid:
            # self.write({'state': 'sent'})
            self.state = 'sent'
        else:
            self.state = 'draft'

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

    def action_mail(self):
        action_id = self.env.ref('hr_requests_new.hr_requests_new_action_window').id
        base_url = self.env.cr.dbname
        link = '/web/#id=%s&view_type=form&model=hr.request&action_id=%s' % (
            self.id, action_id)

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

        if self.emp_id:
            id = self.emp_id
        else:
            id = ''
        if self.date_start:
            joining = self.date_start
        else:
            joining = ''

        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.employee_id.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            id) + "</td></tr>" \
                  "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>" + str(
            x) + "</td></tr></tbody></table><br/>" + \
               "Please review and apply your decision<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        users = self.env['res.users'].search([])
        uids = []
        mailto = ""
        for u in users:
            if u.has_group('hr.group_hr_manager'):
                mailto += str(u.partner_id.email) + ","
                uids.append(u.partner_id.id)
        email_template = self.env['mail.template'].create({
            'name': 'TestTemplate',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': str(self.name) + " to Approve",
            'body_html': body,
            'auto_delete': True
        })

        mail = self.env['mail.template'].browse(email_template.id).send_mail(
            self.employee_id.parent_id.user_id.partner_id.id)
        email_template.unlink()
        # approvers = self.env['hr.employee'].search([('parent_id','=', self.employee_id.parent_id.id)])
        # app_ids = []
        # for a in approvers:
        #     app_ids.append(a.id)
        return self.write({
            'state': 'sent',
            'approver_ids': [(6, 0, [self.employee_id.parent_id.id])]
        })

    def action_approve(self):
        # body = self.name+"Approved"
        # self.employee_id.parent_id.user_id.notify_info(body)
        if self.employee_id.parent_id.user_id.id != self.env.uid and self.type != 'unsuspend':
            raise UserError('Only direct manager can approve this Request')
        if self.employee_id1.parent_id.user_id.id != self.env.uid and self.type == 'unsuspend':
            raise UserError('Only direct manager can approve this Request')
        action_id = self.env.ref('hr_requests_new.hr_requests_new_action_window').id

        link = '/web/#id=%s&view_type=form&model=hr.request&action_id=%s' % (self.id, action_id)
        # body = "<![CDATA[<p>Dear " + '${object.name}' + "<br/> <br/>" \
        #                                                                     "    You have " + str(
        #     self.name) + " to confirm.<br/> Please review and apply your decision " + \
        #        "<a href =\" " + link + "\"> here</a><br/> </p><br/>Regards,<br/>${(object.company_id.name)}"
        # ('unrenew', 'Un Renew Contract'),
        # ('resign', 'Resignation'),
        # ('terminate', 'Termination'),
        # ('promote', 'Promotion'),
        # ('trip', 'Business Trip'),
        # ('suspend', 'Stop Salary'),
        # ('unsuspend', 'Release Salary'),
        # ('letter', 'Letter'),
        # ('penalty', 'Penalty')
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

        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.employee_id.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            id) + "</td></tr>" \
                  "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>" + str(
            x) + "</td></tr></tbody></table><br/>" + \
               "Please review and apply your decision<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + '${object.name}' + \
        #        "<br/><br/>" + "   You are requested to take an action on  " + str(x) + \
        #        " for employee " + str(self.employee_id.name) + ".<br/> Please click" \
        #        "<a href =\" " + link + "\">here</a> to make approval or refusal action.<br/>" + \
        #        "</p><br/>Regards,<br/>${(object.company_id.name)}"
        users = self.env['res.users'].search([])
        uids = []
        apps = []
        mailto = ""
        for u in users:
            if u.has_group('hr_requests_new.group_hr_majid'):
                apps.append(u.id)
                mailto += str(u.partner_id.email) + ","
                uids.append(u.partner_id.id)

        email_template = self.env['mail.template'].create({
            'name': 'ToConfirm',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': str(self.name) + " to approve",
            'body_html': body,
            'auto_delete': True
        })

        for i in uids:
            self.env['mail.template'].browse(email_template.id).send_mail(i)
        email_template.unlink()
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

    def action_majid(self):
        action_id = self.env.ref('hr_requests_new.hr_requests_new_action_window').id
        base_url = self.env.cr.dbname
        link = '/web/#id=%s&view_type=form&model=hr.request&action_id=%s' % (
            self.id, action_id)
        # body = "<![CDATA[<p>Dear " + '${object.name}' + "<br/><br/>""   You have " + str(self.name) \
        #        + " to confirm.<br/> Please review and apply your decision " + "<a href =\" " + link + "\"> here</a><br/>" \
        #        "</p><br/>Regards,<br/>${(object.company_id.name)}"

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

        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.employee_id.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            id) + "</td></tr>" \
                  "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>" + str(
            x) + "</td></tr></tbody></table><br/>" + \
               "Please review and apply your decision<br/></p><br/>Regards,<br/>${(object.company_id.name)}"

        # body = "<![CDATA[<p>Dear " + '${object.name}' + \
        #        "<br/><br/>" + "   You are requested to take an action on  " + str(x) + \
        #        " for employee " + str(self.employee_id.name) + ".<br/> Please click" \
        #        "<a href =\" " + link + "\">here</a> to make approval or refusal action.<br/>" + \
        #        "</p><br/>Regards,<br/>${(object.company_id.name)}"
        users = self.env['res.users'].search([])
        uids = []
        apps = []
        mailto = ""
        for u in users:
            if u.has_group('hr.group_hr_manager'):
                apps.append(u.id)
                mailto += str(u.partner_id.email) + ","
                uids.append(u.partner_id.id)

        email_template = self.env['mail.template'].create({
            'name': 'ToConfirm',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': str(self.name) + " to confirm",
            'body_html': body,
            'auto_delete': True
        })
        for i in uids:
            self.env['mail.template'].browse(email_template.id).send_mail(i)
        email_template.unlink()
        approvers = self.env['hr.employee'].search([('user_id', 'in', apps)])
        app_ids = []
        for a in approvers:
            app_ids.append(a.id)
        return self.write({
            'state': 'majid',
            'approver_ids': [(6, 0, app_ids)]
        })

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

        action_id = self.env.ref('hr_requests_new.hr_requests_new_action_window').id
        base_url = self.env.cr.dbname
        link = '/web/#id=%s&view_type=form&model=hr.request&action_id=%s' % (
            self.id, action_id)
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

        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.employee_id.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            id) + "</td></tr>" \
                  "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>" + str(
            x) + "</td></tr></tbody></table><br/>" + \
               "Your request has been approved<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + str(self.employee_id.name) + ",<br/> Your request for " + str(x) + \
        #        " has been Approved.<br/> Please review " + "<a href =\" " + link + "\"> here</a><br/>" \
        #                                                                    "</p><br/>Regards,<br/>${(object.company_id.name)}"

        email_template = self.env['mail.template'].create({
            'name': 'ConfirmedRequest',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': str(self.name) + " Confirmed",
            'body_html': body,
            'auto_delete': True
        })
        mail = self.env['mail.template'].browse(email_template.id).send_mail(self.employee_id.user_id.partner_id.id)
        email_template.unlink()
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
                self.state == 'sent' and self.type != 'unsuspend':
            raise UserError('Only direct manager and HR Manager can refuse this Request')
        if (not (self.employee_id1.parent_id.user_id.id == self.env.uid or self.env.user.has_group(
                'hr.group_hr_manager'))) and \
                self.state == 'sent' and self.type == 'unsuspend':
            raise UserError('Only direct manager and HR Manager can refuse this Request')
        emp = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        emp1 = self.env['hr.employee'].search([('id', '=', self.employee_id1.id)], limit=1)
        type = ''
        if self.type == 'unrenew':
            type = 'unrenew'
        elif self.type == 'terminate':
            type = 'termination'
        elif self.type == 'resign':
            type = 'resignation'
        if self.type == 'suspend':
            self.employee_id.sudo().write({
                'active': True,
            })
        elif self.type == 'unsuspend':
            self.employee_id1.write({
                'active': False,
            })
        elif self.type in ['unrenew', 'terminate', 'resign']:
            self.env['termination.termination'].search([('end_of_service', '=', self.apply_from),
                                                        ('employee', '=', self.employee_id.id),
                                                        ('name', '=', type)]).unlink()
        action_id = self.env.ref('hr_requests_new.hr_requests_new_action_window').id
        base_url = self.env.cr.dbname
        link = '/web/#id=%s&view_type=form&model=hr.request&action_id=%s' % (
            self.id, action_id)
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

        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.employee_id.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            id) + "</td></tr>" \
                  "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>" + str(
            x) + "</td></tr></tbody></table><br/>" + \
               "Your request has been Rejected<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + str(self.employee_id.name) + ",<br/><br/>""  Your request for " + str(x) + \
        #        " has been Rejected.<br/> Please review " + "<a href =\" " + link + "\"> here</a><br/>" \
        #        "</p><br/>Regards,<br/>${(object.company_id.name)}"

        email_template = self.env['mail.template'].create({
            'name': 'RejectedRequest',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': str(self.name) + " Rejected",
            'body_html': body,
            'auto_delete': True
        })
        mail = self.env['mail.template'].browse(email_template.id).send_mail(self.employee_id.user_id.partner_id.id)
        email_template.unlink()
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
