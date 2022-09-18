from odoo import api, models, fields

from datetime import datetime,date,timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class Holidays(models.Model):
   _inherit = "hr.holidays"

   allocation_date = fields.Date('Allocation Date')

   @api.onchange('date_from')
   def _onchange_date_from(self):
      pass

   @api.onchange('date_to')
   def _onchange_date_to(self):
      pass

   def check_day_on_working_days(self, leave_date):
      week_day = leave_date.weekday()
      day_on_working_days = 0
      if self.employee_id.contract_id and self.employee_id.contract_id.resource_calendar_id.attendance_ids:
         for attendance_id in self.employee_id.contract_id.resource_calendar_id.attendance_ids:
            if week_day == int(attendance_id.dayofweek):
               day_on_working_days = 1
      return day_on_working_days

   def check_day_not_on_holiday(self, leave_date):
      day_not_on_holiday = 1
      national_holidays = self.env['hr.national.holiday'].search([ ('state', '=', 'Confirmed')])
      for holiday in national_holidays:
         if leave_date.strftime("%Y-%m-%d") >= holiday.start_date and leave_date.strftime("%Y-%m-%d") <= holiday.end_date:
            day_not_on_holiday = 0
      return day_not_on_holiday

   def daterange(self, start_date, end_date):
      for n in range(int((end_date - start_date).days + 1)):
         yield start_date + timedelta(n)

   def _get_number_of_days(self, date_from, date_to):
      DATE_FORMAT = "%Y-%m-%d"
      from_dt = datetime.strptime(date_from.split(' ')[0], DATE_FORMAT)
      to_dt = datetime.strptime(date_to.split(' ')[0], DATE_FORMAT)
      timedelta = to_dt - from_dt
      diff_day = timedelta.days  # + float(timedelta.seconds) / 86400
      return diff_day

   @api.onchange('date_to', 'date_from' )
   def onchange_period_custom(self):
      for rec in self:
         date_from = rec.date_from
         date_to = rec.date_to

         # Compute and update the number of days
         if date_to and date_from:
            # ///////// Check if working days or calendar days
            working_calendar = self.holiday_status_id.working_calendar or 'Working Days'
            if working_calendar == 'Working Days':
               if rec.employee_id.contract_id.resource_calendar_id.attendance_ids:
                  date_from_date = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
                  date_to_date = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
                  working_days = 0
                  for leave_date in self.daterange(date_from_date, date_to_date):
                     if self.check_day_on_working_days(leave_date):
                        if self.check_day_not_on_holiday(leave_date):
                           working_days += 1
                  rec.number_of_days_temp = working_days

            if working_calendar == 'Calendar days':
               national_holidays = self.env['hr.national.holiday'].search([('state', '=', 'Confirmed')])
               total_conflict_days = 0
               for holiday in national_holidays:
                  if holiday.end_date < date_from.split(' ')[0] or holiday.start_date > date_to.split(' ')[0]:
                     continue
                  else:
                     if holiday.start_date > date_from:
                        conflict_start = holiday.start_date
                     else:
                        conflict_start = date_from

                     if holiday.end_date < date_to:
                        conflict_end = holiday.end_date
                     else:
                        conflict_end = date_to
                     if not holiday.branches or rec.employee_id.branch_id.id in holiday.branches.ids:
                        conflict_days = rec._get_number_of_days(conflict_start, conflict_end) + 1
                        total_conflict_days += conflict_days
               diff_day = self._get_number_of_days(date_from, date_to)
               rec.number_of_days_temp = round(math.floor(diff_day)) + 1 - total_conflict_days
         else:
            rec.number_of_days_temp = 0

   @api.constrains('state', 'number_of_days_temp', 'holiday_status_id')
   def _check_holidays(self):
      for holiday in self:
         if holiday.holiday_type != 'employee' or holiday.type != 'remove' or not holiday.employee_id or holiday.holiday_status_id.limit or holiday.holiday_status_id.allocation_type == 'On Demand':
            continue
         leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
         if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                 float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
            raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                    'Please verify also the leaves waiting for validation.'))

   @api.constrains('employee_id','holiday_status_id','number_of_days_temp')
   def check_allocation(self):
      for rec in self:
         if rec.holiday_status_id.gender == 'Male only' and rec.employee_id.gender != 'male':
            raise ValidationError('Selected leave type only allowed for males')
         if rec.holiday_status_id.gender == 'Females only' and rec.employee_id.gender != 'female':
            raise ValidationError('Selected leave type only allowed for females')
         # ALlocations checks
         if rec.type == 'add':
            if rec.holiday_status_id.allocation_type == 'On Demand' or rec.limit:
               raise ValidationError('Leaves of type on demand and unlimited balance can not have allocation ')
            if rec.holiday_status_id.allocation_type == 'One Time':
               taken_before = self.search([('employee_id','=',rec.employee_id.id),('holiday_status_id','=',rec.holiday_status_id.id),('state','=','validate'), ('type', '=', 'add')])
               if taken_before:
                  raise ValidationError('Employee Has allocation for this one time leave before')
            if rec.number_of_days_temp > rec.holiday_status_id.allocation_days:
               raise ValidationError('Number Of Days allocated must be less than leave type allocation days')
         # Leave requests checks
         if rec.type == 'remove':
            if rec.holiday_status_id.separated == 'Only Continued' and rec.number_of_days_temp != rec.holiday_status_id.allocation_days:
               raise ValidationError('This leave must be taken continued in one leave not separated')
            if rec.holiday_status_id.separated == 'Only Separated' and rec.number_of_days_temp > rec.holiday_status_id.max_request:
               raise ValidationError('You can not exceed max number of days per request for this leave type')



   @api.model
   def cron_allocatiions(self):
      allocations = []
      for contract in self.env['hr.contract'].search([]):
         for leave_type in self.env['hr.holidays.status'].search([('limit','=',False),('allocation_type','!=','On Demand'),]):
            if contract.employee_id.gender == 'male' and leave_type.gender == 'Females only':
               continue
            if contract.employee_id.gender == 'female' and leave_type.gender == 'Male only':
               continue
            if leave_type.allocation_type == 'One Time':
               taken_before = self.env['hr.holidays'].search(
                  [('employee_id', '=', contract.employee_id.id), ('holiday_status_id', '=', leave_type.id),
                   ('state', '=', 'validate'), ('type', '=', 'add')])
               if not taken_before:
                  allocations.append({
                     'name': 'Automatic Allocation By The System',
                     'allocation_date': date.now(),
                     'holiday_status_id': leave_type.id,
                     'employee_id': contract.employee_id.id,
                     'number_of_days_temp': leave_type.allocation_days,
                  })
            else:
               create_allocation = True
               allocation_days = leave_type.allocation_days
               last_allocation_date = False
               last_allocation = self.env['hr.holidays'].search(
                  [('employee_id', '=', contract.employee_id.id), ('holiday_status_id', '=', leave_type.id),
                   ('state', '=', 'validate'), ('type', '=', 'add')],order="allocation_date desc", limit=1)
               if last_allocation and last_allocation.allocation_date:
                  last_allocation_date = last_allocation.allocation_date
                  last_allocation_date_plus_year = last_allocation_date + relativedelta(years=1)
                  last_year_allocations_count = 0
                  last_year_allocations = self.env['hr.holidays'].search(
                     [('employee_id', '=', contract.employee_id.id), ('holiday_status_id', '=', leave_type.id),
                      ('state', '=', 'validate'), ('type', '=', 'add'), ('allocation_date', '>=', last_allocation_date), ('allocation_date', '<', last_allocation_date_plus_year)])
                  if last_year_allocations:
                     last_year_allocations_count = sum(l.number_of_days_temp for l in last_year_allocations)
                  if leave_type.allocation_type == 'Yearly':
                     last_allocation_date_plus_years = last_allocation_date + relativedelta(years=leave_type.allocate_every)
                     if date.now() < last_allocation_date_plus_years:
                        create_allocation = False
                  if leave_type.allocation_type == 'Monthly':
                     allocation_days = leave_type.allocate_every_days
                     last_allocation_date_plus_month = last_allocation_date + relativedelta(months=leave_type.allocate_every)
                     if date.now() < last_allocation_date_plus_month or last_year_allocations_count >= leave_type.allocation_days:
                        create_allocation = False
                  if leave_type.allocation_type == 'Daily':
                     allocation_days = leave_type.allocate_every_days
                     last_allocation_date_plus_day = last_allocation_date + relativedelta(days=leave_type.allocate_every)
                     if date.now() < last_allocation_date_plus_day  or last_year_allocations_count >= leave_type.allocation_days:
                        create_allocation = False

               if create_allocation and allocation_days != 0:
                  allocations.append({
                     'name': 'Automatic Allocation By The System',
                     'allocation_date': date.now(),
                     'holiday_status_id': leave_type.id,
                     'employee_id': contract.employee_id.id,
                     'number_of_days_temp': allocation_days,
                  })