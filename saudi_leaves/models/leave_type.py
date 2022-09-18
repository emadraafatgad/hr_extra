from odoo import api, models, fields


class LeaveType(models.Model):
   _name = "hr.holidays.status"
   _inherit = ['hr.holidays.status','mail.thread']

   type = fields.Selection([
      ('Annual', 'Annual'),
      ('Non Annual', 'Non Annual'),
   ], string='Type',default='Annual')
   separated = fields.Selection([
      ('Only Separated', 'Only Separated'),
      ('Only Continued', 'Only Continued'),
      ('Both', 'Both'),
   ], string='Can Be Separated',default='Both')
   max_request = fields.Integer('Max Per Request',help='Max Number of days at one request', default=1)
   reconciliation_method = fields.Selection([('Paid','Paid'),
                                             ('Unpaid','Unpaid')],
                                            string='Leave Reconciliation method',default='Paid')

   gender = fields.Selection([
      ('Male only', 'Male only'),
      ('Females only', 'Females only'),
      ('Both', 'Both'),
   ], string='Who Can Request',default='Both')

   allocation_type = fields.Selection([
      ('One Time', 'One Time'),
      ('On Demand', 'On Demand'),
      ('Yearly', 'Yearly'),
      ('Monthly', 'Monthly'),
      ('Daily', 'Daily'),
   ], string='Allocation Type')
   allocate_every = fields.Integer('Allocate Every', default=1 ,help='Period Of (days/months/years) to allocate every')
   allocate_every_days = fields.Float('Allocate Every Days', help='number of days to allocate every (days/months/years) ')
   allocation_days = fields.Float('Allocation Days')
   working_calendar = fields.Selection([
      ('Working Days', 'Working Days'),
      ('Calendar days', 'Calendar days'),
   ], string='Working / Calendar')
   # nationality = fields.Selection([
   #    ('Native', 'Native Only'),
   #    ('Non-native', 'Non-native Only'),
   #    ('All Nationalities', '‫All Nationalities‬‬'),
   # ], 'Nationality')

   @api.onchange('type')
   def onchange_type(self):
      for rec in self:
         if rec.type == 'Annual':
            rec.reconciliation_method = 'Paid'
            rec.separated = 'Both'

   @api.onchange('limit')
   def onchange_limit(self):
      for rec in self:
         if rec.limit:
            rec.separated = False


