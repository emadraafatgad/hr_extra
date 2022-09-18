# from datetime import datetime
from odoo import models, fields


class HrAttendanceSheet(models.Model):
    _name = "hr.attendance.config"

    name = fields.Char("NAME")
    f_time_from = fields.Float(string="Time From")
    f_time_to = fields.Float(string="Time To")
    f_hours = fields.Float(string="Ded Hours", help="First Deduction hours per day")
    s_time_from = fields.Float(string="Time From")
    s_time_to = fields.Float(string="Time To")
    s_hours = fields.Float(string="Ded Hours", help="Sec Deduction hours per day")
    Authorization_request = fields.Float()
