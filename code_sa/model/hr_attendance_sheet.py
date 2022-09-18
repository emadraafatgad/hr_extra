import datetime

from odoo import models, fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'
    _rec_name = "employee_id"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    em_attendance = fields.Many2many('hr.attendance', string="attendance")
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', index=True)
    date_from = fields.Datetime()
    date_to = fields.Datetime()

    def action_get_attendance(self):
        attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        emp_attendance = []
        print(attendance_ids)
        attendance_from_date = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT).strftime(
            "%Y-%m-%d")
        attendance_to_date = datetime.datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT).strftime(
            "%Y-%m-%d")

        # for date in range(0, 31, 1):
        #     print(date, "-")
        #     next_date = (datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)+ timedelta(days=date+1))
        #     print(next_date)

        for attendance in attendance_ids:
            attendance_date = datetime.datetime.strptime(attendance.write_date,
                                                         DEFAULT_SERVER_DATETIME_FORMAT).strftime("%Y-%m-%d")
            if attendance_date >= attendance_from_date and attendance_date <= attendance_to_date:
                print(attendance.write_date)
                # attendance_day = attendance_date.weekday()
                # print(attendance_day, "day")
                # if self.action_submit_to_manager(attendance_date ,attendance_day):
                emp_attendance.append(attendance.id)
                # else:
                #     emp_attendance.date_from
        # print(emp_attendance)
        self.em_attendance = [(6, 0, emp_attendance)]

    def action_submit_to_manager(self, attendance_date, attendance_day):
        attendance_day = attendance_day + 1
        # print(attendance_day)
        if attendance_day == 7:
            attendance_day = 0
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        # print(contract.resource_calendar_id.attendance_ids)
        # day_int = datetime.datetime.strptime(self.check_out, DEFAULT_SERVER_DATETIME_FORMAT).weekday()
        for contract_date in contract.resource_calendar_id.attendance_ids:
            # print(int(contract_date.dayofweek),"day1")
            if int(contract_date.dayofweek) == int(attendance_day):
                print(contract_date.name, "day name")
                print(contract_date.date_from)
                print(contract_date.date_to)
                return True

    def cheack_working_days(self, day_date):
        date_day = day_date.weekday()
        date_day = date_day + 1
        # print(attendance_day)
        if date_day == 7:
            date_day = 0
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        for contract_date in contract.resource_calendar_id.attendance_ids:
            if int(contract_date.dayofweek) == int(date_day):
                print(contract_date.date_from)
                print(contract_date.date_to)

    # def Duration(self, date_day):
    #     # print(date_day)
    #     date_day = date_day.strftime("%Y-%m-%d")
    #     # print(date_day,"====================")
    #     attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
    #     print(attendance_ids)
    #     # attendance_ids = attendance_ids.search(['&',('write_date','>=',self.date_from),("write_date','<=",self.date_to)])
    #     print(attendance_ids)
    #     for attendance in attendance_ids:
    #
    #         attendance_date = datetime.datetime.strptime(attendance.write_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime("%Y-%m-%d")
    #         # if attendance_date >=
    #         if str(date_day) == str(attendance_date):
    #             print(attendance_date, "2018")
    #             print(date_day, "??")
    #         else:
    #             print("Not Found In Attendance")
    #     print(",,,,,,,,,,,,,,,,")
    # number_of_days_temp
