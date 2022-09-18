import datetime

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class HrPayroll(models.Model):
    _inherit = 'hr.payslip'

    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True, store=True)
    attendance_sheet = fields.Many2many("hr.attendance", readonly=True)
    working_days = fields.Float()
    absence_days = fields.Float()
    working_hours = fields.Float()
    over_time_hours = fields.Float()
    deduct_hours = fields.Float()
    permissions_hours = fields.Float()
    net_deduct_hours = fields.Float()
    unpaid_leave_days = fields.Float()

    @api.onchange('deduct_hours', 'permissions_hours')
    def onchange_duduct(self):
        if self.deduct_hours > self.permissions_hours:
            self.net_deduct_hours = self.deduct_hours - self.permissions_hours
        else:
            self.net_deduct_hours = 0

    # @api.multi
    # def compute_sheet(self):
    #     for payslip in self:
    #         number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
    #         #delete old payslip lines
    #         payslip.line_ids.unlink()
    #         # set the list of contract for which the rules have to be applied
    #         # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
    #         contract_ids = payslip.contract_id.ids or \
    #             self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
    #         lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
    #         payslip.write({'line_ids': lines, 'number': number})
    #         payslip.action_get_attendance()
    #     return True

    def action_get_attendance(self):
        attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        permission_ids = self.env['exemption.exemption'].search(
            [('name', '=', self.employee_id.id), ('state', '=', 'done')])
        emp_attendance = []
        print(attendance_ids)
        attendance_from_date = self.date_from
        attendance_to_date = self.date_to
        working = 0.0
        absence = 0.0
        unpaid_leave = 0.0
        working_hours = 0.0
        over_time_hours = 0.0
        deduct_hours = 0.0
        permissions_hours = 0
        for attendance in attendance_ids:
            attendance_date = datetime.datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT).strftime(
                "%Y-%m-%d")
            if attendance_date >= attendance_from_date and attendance_date <= attendance_to_date:
                # print(attendance.check_in)
                emp_attendance.append(attendance.id)
                if attendance.state == "absent":
                    absence = absence + 1
                elif attendance.state == "unpaid leave":
                    unpaid_leave = unpaid_leave + 1
                else:
                    working = working + 1
                over_time_hours = over_time_hours + attendance.over_time
                working_hours = working_hours + attendance.worked_hours
                deduct_hours = deduct_hours + attendance.deduct_time
        for permission in permission_ids:
            permission_date = datetime.datetime.strptime(permission.date, DEFAULT_SERVER_DATE_FORMAT).strftime(
                "%Y-%m-%d")
            if permission_date >= attendance_from_date and permission_date <= attendance_to_date:
                # print(permission.check_in)
                permissions_hours = permissions_hours + permission.late_hours

        # print(emp_attendance)
        self.absence_days = absence
        self.working_days = working
        self.unpaid_leave_days = unpaid_leave
        self.over_time_hours = over_time_hours
        self.deduct_hours = deduct_hours
        self.permissions_hours = permissions_hours
        if deduct_hours > permissions_hours:
            self.net_deduct_hours = deduct_hours - permissions_hours
        else:
            self.net_deduct_hours = 0
        self.working_hours = working_hours
        self.attendance_sheet = [(6, 0, emp_attendance)]
