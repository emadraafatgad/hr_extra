from odoo import fields, models


class HrEmployeeMeeting(models.Model):
    _name = 'hr.meeting'

    name = fields.Char(string="Reason", required=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    meeting_from = fields.Datetime(required=True)
    meeting_to = fields.Datetime(required=True)
    notes = fields.Text(string="Note")
