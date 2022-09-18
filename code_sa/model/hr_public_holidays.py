from odoo import fields, models


class HrPublicHolidays(models.Model):
    _name = "hr.holiday"

    name = fields.Char(string="Reason", required=True)
    start_date = fields.Datetime(string="From", required=True)
    end_date = fields.Datetime(string="To", required=True)
    notes = fields.Text(string="Note")


class HrEmployeeMeeting(models.Model):
    _name = 'hr.meeting'

    name = fields.Char(string="Reason", required=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    meeting_from = fields.Datetime(required=True)
    meeting_to = fields.Datetime(required=True)
    notes = fields.Text(string="Note")


class Hrpayroll_attendance(models.Model):
    _inherit = "hr.payslip"
    commission = fields.Float(default=1000)
