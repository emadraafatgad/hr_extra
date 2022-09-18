from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ResourceCalendarAttendance(models.Model):
    _name = "resource.calendar.attendance"
    _description = "Work Detail"
    _order = 'dayofweek, hour_from'

    dayofweek = fields.Selection([
        ('0', 'Sunday'),
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
    ], 'Day of Week', required=True, index=True, default='0')

    name = fields.Char(required=True)
    date_from = fields.Date(string='Starting Date')
    date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.")
    hour_from_limit = fields.Float(string="Work from limit", required=True, index=True,
                                   help="Start and End time of working.")
    hour_to = fields.Float(string='Work to', required=True)
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=True, ondelete='cascade')


def hours_time_string(hours):
    """ convert a number of hours (float) into a string with format '%H:%M' """
    minutes = int(round(hours * 60))
    return "%02d:%02d" % divmod(minutes, 60)


class HrHolidaySummaryReport(models.AbstractModel):
    _inherit = 'report.hr_holidays.report_holidayssummary'
    _name = 'report.hr_holidays.report_holidayssummary'

    def _get_day(self, start_date):
        res = []
        start_date = fields.Date.from_string(start_date)
        for x in range(0, 60):
            color = '#ababab' if start_date.strftime('%a') == 'Sat' or start_date.strftime('%a') == 'Fri' else ''
            res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day, 'color': color})
            start_date = start_date + relativedelta(days=1)
        return res

    def _get_leaves_summary(self, start_date, empid, holiday_type):
        res = []
        count = 0
        start_date = fields.Date.from_string(start_date)
        end_date = start_date + relativedelta(days=59)
        for index in range(0, 60):
            current = start_date + timedelta(index)
            res.append({'day': current.day, 'color': ''})
            if current.strftime('%a') == 'Sat' or current.strftime('%a') == 'Fri':
                res[index]['color'] = '#ababab'
        # count and get leave summary details.
        holiday_type = ['confirm', 'validate'] if holiday_type == 'both' else [
            'confirm'] if holiday_type == 'Confirmed' else ['validate']
        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', empid), ('state', 'in', holiday_type),
            ('type', '=', 'remove'), ('date_from', '<=', str(end_date)),
            ('date_to', '>=', str(start_date))
        ])
        for holiday in holidays:
            # Convert date to user timezone, otherwise the report will not be consistent with the
            # value displayed in the interface.
            date_from = fields.Datetime.from_string(holiday.date_from)
            date_from = fields.Datetime.context_timestamp(holiday, date_from).date()
            date_to = fields.Datetime.from_string(holiday.date_to)
            date_to = fields.Datetime.context_timestamp(holiday, date_to).date()
            for index in range(0, ((date_to - date_from).days + 1)):
                if date_from >= start_date and date_from <= end_date:
                    res[(date_from - start_date).days]['color'] = holiday.holiday_status_id.color_name
                date_from += timedelta(1)
            count += abs(holiday.number_of_days)
        self.sum = count
        return res
