# from datetime import datetime
import calendar
import datetime

import pytz

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResourceCalender(models.Model):
    _inherit = "resource.calendar"

    max_sign_in = fields.Float("Max late sign in", default=0)


class HrAttendanceSheet(models.Model):
    _inherit = "hr.attendance"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    # planned_worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    state = fields.Selection(
        [('working day', 'Working day'),
         ('absent', 'Absent'),
         ('week end', 'Week End'),
         ('unpaid leave', 'Unpaid Leave'),
         ('paid leave', 'paid leave'),
         ('Public Holiday', 'Public Holiday')],
    )
    day = fields.Char()
    planned_sign_in = fields.Float()
    sign_in_limit = fields.Float()
    planned_sign_ou = fields.Float()
    late_in = fields.Float()
    # s_ov_time = fields.Float("Special Overtime")
    deduct_time = fields.Float("Deduction (Hours)")
    over_time = fields.Float()
    early_sign_out = fields.Float()
    note = fields.Text()

    @api.onchange('check_in', 'employee_id', 'check_out')
    def _set_attendance_normal_info(self):

        for attendance in self:
            user_pool = self.env['res.users']
            user = user_pool.browse(self.env.uid)
            tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            day_int = datetime.datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT).weekday()
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', attendance.employee_id.id), ('state', '=', 'open')], limit=1)
            attendance_rule = self.env["hr.attendance.config"].search([], limit=1)
            if day_int < 6:
                day_no = day_int + 1
                day_str = calendar.day_name[day_int]
            elif day_int == 6:
                day_no = 0
                day_str = calendar.day_name[day_int]
            attendance.day = day_str
            counter = 0
            today_int = datetime.datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT).weekday()
            if today_int < 6:
                day_no = today_int + 1
                day_str = calendar.day_name[today_int]
            elif today_int == 6:
                day_no = 0
            check_in_time = pytz.utc.localize(
                datetime.datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
            time_in = check_in_time.hour + check_in_time.minute / 60.0
            if attendance.check_out and attendance.check_in:
                check_out_time = pytz.utc.localize(
                    datetime.datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
                time_out = check_out_time.hour + check_out_time.minute / 60.0
                delta = datetime.datetime.strptime(attendance.check_out,
                                                   DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                delta = 0
                time_out = 0
            if contract:
                if contract.resource_calendar_id:
                    x = 0
                    for line in contract.resource_calendar_id.attendance_ids:
                        counter = counter + 1
                        if int(line.dayofweek) == int(day_no):
                            x = 1
                            attendance.planned_sign_in = line.hour_from
                            attendance.planned_sign_ou = line.hour_to
                            wh = line.hour_to - line.hour_from
                            # attendance.s_ov_time = 0
                            attendance.sign_in_limit = line.hour_from + contract.resource_calendar_id.max_sign_in
                            if time_out:
                                if attendance.worked_hours > wh:
                                    attendance.early_sign_out = 0
                                    attendance.over_time += attendance.worked_hours - wh
                                    attendance.deduct_time = 0
                                elif attendance.worked_hours < wh:
                                    attendance.early_sign_out = wh - attendance.worked_hours
                                    attendance.deduct_time = wh - attendance.worked_hours
                                    attendance.over_time = 0
                                else:
                                    attendance.early_sign_out = 0
                                    attendance.over_time = 0
                                    attendance.deduct_time = 0
                            else:
                                attendance.early_sign_out = 0
                                attendance.over_time = 0
                                attendance.deduct_time = 0
                            if time_in <= line.hour_from + contract.resource_calendar_id.max_sign_in:
                                attendance.late_in = 0
                                if attendance.worked_hours > wh:
                                    attendance.over_time += line.hour_from - time_in
                            else:
                                attendance.late_in = time_in - line.hour_from - contract.resource_calendar_id.max_sign_in

                            # attendance.deduct_time = attendance.early_sign_out + attendance.late_in
                    if not x:
                        # if delta:
                        #     attendance.s_ov_time = delta.total_seconds() / 3600.0
                        attendance.late_in = 0
                        attendance.early_sign_out = 0
                        attendance.over_time = 0
                        attendance.deduct_time = 0
                        attendance.planned_sign_in = 0
                        attendance.planned_sign_ou = 0
                        attendance.sign_in_limit = 0
                else:
                    # attendance.s_ov_time = 0
                    attendance.late_in = 0
                    attendance.early_sign_out = 0
                    attendance.over_time = 0
                    attendance.deduct_time = 0
                    attendance.planned_sign_in = 0
                    attendance.planned_sign_ou = 0
                    attendance.sign_in_limit = 0
            else:
                # attendance.s_ov_time = 0
                attendance.late_in = 0
                attendance.early_sign_out = 0
                attendance.over_time = 0
                attendance.deduct_time = 0
                attendance.planned_sign_in = 0
                attendance.planned_sign_ou = 0
                attendance.sign_in_limit = 0

                # if attendance_rule:
                #     if int(line.dayofweek) == int(day_no):
                #         # print(attendance_rule.f_time_from)
                #         # print(time_in, "time in")
                #         # print(attendance_rule.f_time_to)
                #         # print(time_in > attendance_rule.f_time_from)
                #         # print(time_in <= attendance_rule.f_time_to)
                #         # print(time_in > attendance_rule.s_time_from)
                #         # print(time_in <= attendance_rule.s_time_to)
                #         # print(time_in > attendance_rule.s_time_to)
                #         if time_in < attendance_rule.f_time_from:
                #             # print("early come ")
                #             attendance.deduct_time = 0
                #             # print(attendance.deduct_time)
                #         elif time_in > attendance_rule.f_time_from and time_in <= attendance_rule.f_time_to:
                #             # print("latency phase 1 = ", time_in - attendance_rule.f_time_from)
                #             attendance.late_in = time_in - attendance_rule.f_time_from
                #             attendance.deduct_time = 2
                #             # print(attendance.deduct_time)
                #         elif time_in > attendance_rule.s_time_from and time_in <= attendance_rule.s_time_to:
                #             # print("latency phase 2= ", time_in - attendance_rule.f_time_from)
                #             attendance.late_in = time_in - attendance_rule.f_time_from
                #             attendance.deduct_time = 4
                #             # print(attendance.deduct_time)
                #         elif time_in > attendance_rule.s_time_to:
                #             # print("latency phase 3 ", time_in - attendance_rule.f_time_from)
                #             attendance.late_in = time_in - attendance_rule.f_time_from
                #             attendance.deduct_time = 8
                #             # print(attendance.deduct_time)
                #         else:
                #             # print("early come ")
                #             attendance.deduct_time = 0
                #             # print(attendance.deduct_time)

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        user_pool = self.env['res.users']
        user = user_pool.browse(self.env.uid)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        # attendance_rule = self.env["hr.attendance.config"].search([],limit=1)
        # attendance_rule =attendance_rules[0]
        # get time zone times

        for attendance in self:
            if attendance.check_out:
                # if attendance_rule:
                #     attendance.sign_in_limit = attendance_rule.f_time_from

                delta = datetime.datetime.strptime(attendance.check_out,
                                                   DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                # print(delta)

                check_out_time = pytz.utc.localize(
                    datetime.datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
                time_out = check_out_time.hour + check_out_time.minute / 60.0
                # print(delta.total_seconds() / 3600.0,"total hours")
                # print(attendance.check_out)
                # beacouse it of not using tz
                day_int = datetime.datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT).weekday()
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', attendance.employee_id.id), ('state', '=', 'open')], limit=1)
                if day_int < 6:
                    day_no = day_int + 1
                    day_str = calendar.day_name[day_int]
                elif day_int == 6:
                    day_no = 0
                    day_str = calendar.day_name[day_int]
                counter = 0
                x = 0
                today_int = datetime.datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT).weekday()
                if today_int < 6:
                    day_no = today_int + 1
                    day_str = calendar.day_name[today_int]
                elif today_int == 6:
                    day_no = 0
                if contract.resource_calendar_id:
                    for line in contract.resource_calendar_id.attendance_ids:
                        counter = counter + 1
                        if int(line.dayofweek) == int(day_no):
                            attendance.worked_hours = delta.total_seconds() / 3600.0
                            x = 1
                    if not x:
                        attendance.worked_hours = 0
                else:
                    attendance.worked_hours = delta.total_seconds() / 3600.0
                # print(attendance.worked_hours)
                contract = self.env['hr.contract'].search([('employee_id', '=', attendance.employee_id.id)], limit=1)
                # print(contract.resource_calendar_id.name)
                counter = 0
                # for line in contract.resource_calendar_id.attendance_ids:
                #         if time_out > line.hour_to:
                #             attendance.over_time = time_out - line.hour_to
                #             attendance.early_sign_out = 0.0
                #             # print("over time = ", time_out - line.hour_to)
                #         else:
                #             attendance.over_time = 0.0
                #             attendance.early_sign_out = line.hour_to - time_out
                #             # print("early sign out = ", line.hour_to - time_out)
                #         break
