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
        ('sent', 'Sent'),
        ('approve', 'Approved by Level 1'),
        ('majid', 'Approved by Level 2'),
        ('done', 'Approved'),
        ('cancel', 'Rejected'),
    ], string='Status', track_visibility='onchange')
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

    @api.onchange('name')
    def _change_state(self):
        if self.name.parent_id.user_id.id == self.env.uid:
            # self.write({'state': 'sent'})
            self.state = 'sent'
        else:
            self.state = 'draft'

    def action_mail(self):
        action_id = self.env.ref('exemption.action_exemption_exemption_form').id
        link = '/web/#id=%s&view_type=form&model=exemption.exemption&action_id=%s' % (
            self.id, action_id)
        date_start = self.env['hr.contract'].search([('employee_id', '=', self.name.id), ('state', '=', 'open')],
                                                    limit=1).date_start
        if date_start:
            joining = date_start
        else:
            joining = ''
        if self.emp_id:
            identification_id = self.emp_id
        else:
            identification_id = ''
        if self.type == 'late':
            type = 'Late Sign in'
        elif self.type == 'earl':
            type = 'Early Sign out'
        else:
            type = 'Other'

        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.name.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            identification_id) + "</td></tr>" \
                                 "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>Leave Request(" + str(
            type) + ")</td></tr></tbody></table><br/>" + \
               "Please review and apply your decision<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + str(self.name.parent_id.name) + \
        #        "<br/><br/>" + "   You have " + str(self.name.name) + " "+ str(self.late_hours) + \
        #        " hours permission to Approve.<br/> Please review and apply your decision" \
        #         "<a href =\" " + link + "\"> here</a> <br/>" + "</p><br/>Regards,<br/>${(object.company_id.name)}"

        email_template = self.env['mail.template'].create({
            'name': 'TestTemplate',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': str(self.name.name) + " permission to Approve",
            'body_html': body,
            'auto_delete': True
        })
        mail = self.env['mail.template'].browse(email_template.id).send_mail(
            self.name.parent_id.user_id.partner_id.id)
        email_template.unlink()
        return self.write({
            'state': 'sent',
            'approver_ids': [(6, 0, [self.name.parent_id.id])]
        })

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
        date_start = self.env['hr.contract'].search([('employee_id', '=', self.name.id), ('state', '=', 'open')],
                                                    limit=1).date_start
        if date_start:
            joining = date_start
        else:
            joining = ''
        if self.emp_id:
            identification_id = self.emp_id
        else:
            identification_id = ''
        if self.type == 'late':
            type = 'Late Sign in'
        elif self.type == 'earl':
            type = 'Early Sign out'
        else:
            type = 'Other'
        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.name.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            identification_id) + "</td></tr>" \
                                 "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>Leave Request(" + str(
            type) + ")</td></tr></tbody></table><br/>" + \
               "Your permission request has been Approved.<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + str(self.name.name) + ",<br/> Your permission request " + \
        #        "has been Approved.<br/> Please review."\
        #         "<br/></p><br/>Regards,<br/>${(object.company_id.name)}"

        email_template = self.env['mail.template'].create({
            'name': 'ConfirmedRequest',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': "Permission request confirmed",
            'body_html': body,
            'auto_delete': True
        })
        mail = self.env['mail.template'].browse(email_template.id).send_mail(self.name.user_id.partner_id.id)
        email_template.unlink()
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
        # action_id = self.env.ref('hr_requests_new.hr_requests_new_action_window').id
        #
        # link = '/web/#id=%s&view_type=form&model=hr.request&action_id=%s' % (self.id, action_id)
        date_start = self.env['hr.contract'].search([('employee_id', '=', self.name.id), ('state', '=', 'open')],
                                                    limit=1).date_start
        if date_start:
            joining = date_start
        else:
            joining = ''
        if self.emp_id:
            identification_id = self.emp_id
        else:
            identification_id = ''
        if self.type == 'late':
            type = 'Late Sign in'
        elif self.type == 'earl':
            type = 'Early Sign out'
        else:
            type = 'Other'
        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.name.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            identification_id) + "</td></tr>" \
                                 "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>Leave Request(" + str(
            type) + ")</td></tr></tbody></table><br/>" + \
               "Please review and apply your decision.<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + '${object.name}' + \
        #        "<br/><br/>" + "   You are requested to take an action on permission request"  + \
        #        " for employee " + str(self.name.name) + ".<br/> Please click" \
        #        "<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
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
            'subject': "Permission request For" + str(self.name.name) + " to approve",
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
        # return self.write({'state': 'approve'})

    def action_majid(self):
        date_start = self.env['hr.contract'].search([('employee_id', '=', self.name.id), ('state', '=', 'open')],
                                                    limit=1).date_start
        if date_start:
            joining = date_start
        else:
            joining = ''
        if self.emp_id:
            identification_id = self.emp_id
        else:
            identification_id = ''
        if self.type == 'late':
            type = 'Late Sign in'
        elif self.type == 'earl':
            type = 'Early Sign out'
        else:
            type = 'Other'
        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.name.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            identification_id) + "</td></tr>" \
                                 "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>Leave Request(" + str(
            type) + ")</td></tr></tbody></table><br/>" + \
               "Please review and apply your decision.<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + '${object.name}' + \
        #        "<br/><br/>" + "   You are requested to take an action on Permission request" + \
        #        " for employee " + str(self.name.name) + ".<br/> Please click" \
        #        "<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
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
            'subject': "Permission Request for " + str(self.name.name) + " to confirm",
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
        # return self.write({'state': 'majid'})

    def action_cancel(self):
        if (not (self.name.parent_id.user_id.id == self.env.uid or self.env.user.has_group('hr.group_hr_manager'))) and \
                self.state == 'draft':
            raise UserError('Only direct manager and HR Manager can refuse this Request')
        date_start = self.env['hr.contract'].search([('employee_id', '=', self.name.id), ('state', '=', 'open')],
                                                    limit=1).date_start
        if date_start:
            joining = date_start
        else:
            joining = ''
        if self.emp_id:
            identification_id = self.emp_id
        else:
            identification_id = ''
        if self.type == 'late':
            type = 'Late Sign in'
        elif self.type == 'earl':
            type = 'Early Sign out'
        else:
            type = 'Other'
        body = "<![CDATA[<p>Dear " + '${object.name},' + \
               "<br/><br/><br/>Details" + "<table style='width:100%;'><tbody> <tr><td style='width:30%;background-color: #c0c0c0'/> <td style='background-color: #c0c0c0'><strong>Proposed</strong></td></tr>" \
                                          "<tr><td style='width:30%;background-color: #c0c0c0'><strong>Employee Name</td><td style='background-color: #ddd4d4'> " + \
               str(
                   self.name.name) + "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong> Joining Date</strong></td><td style='background-color: #ddd4d4'>" + str(
            joining) + \
               "</td></tr><tr><td style='width:30%;background-color: #c0c0c0'><strong>National identifier</strong></td><td style='background-color: #ddd4d4'>" + str(
            identification_id) + "</td></tr>" \
                                 "<tr><td  style='width:30%;background-color: #c0c0c0'><strong>Request Type</strong></td><td style='background-color: #ddd4d4'>Leave Request(" + str(
            type) + ")</td></tr></tbody></table><br/>" + \
               "Your permission request has been Rejected.<br/></p><br/>Regards,<br/>${(object.company_id.name)}"
        # body = "<![CDATA[<p>Dear " + str(self.name.name) + ",<br/><br/>""  Your permission request " + \
        #        "has been Rejected.<br/> Please review." \
        #       "<br/></p><br/>Regards,<br/>${(object.company_id.name)}"

        email_template = self.env['mail.template'].create({
            'name': 'RejectedRequest',
            'email_from': '${object.company_id and object.company_id.email or ''}',
            'email_to': '${object.email|safe}',
            # 'partner_to': '%s' % self.test_partner.id,
            'model_id': self.env.ref("base.model_res_partner").id,
            'subject': "Permission request refused",
            'body_html': body,
            'auto_delete': True
        })
        mail = self.env['mail.template'].browse(email_template.id).send_mail(self.name.user_id.partner_id.id)
        email_template.unlink()
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
