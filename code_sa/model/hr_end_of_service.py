from odoo import fields, models


class HrContractDate(models.Model):
    _inherit = 'hr.contract'

    joined_date = fields.Date("Joined Date")

# class HrEndOfService(models.Model):
#     _name = "hr.eos"
#     employee = fields.Char()
#     employee_id = fields.Many2one('hr.employee',string="Employee")
#     type = fields.Selection([('Resignation','Resignation'),('Termination','Termination')])
#     joined_date = fields.Date(readonly=True)
#     last_working_day = fields.Date(string="Last Working Day")
#     total_employee_duration = fields.Char(string="Total Employee Duration",readonly=True)
#     remaining_leaves = fields.Char()
#     deductions = fields.Char()
#     eos_amount = fields.Char(string="End Of Service Amount")
#
#     def action_get_eos_amount(self):
#         contract_obj = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)],limit=1)
#         print(contract_obj.joined_date)
#         self.joined_date = contract_obj.joined_date
#         start_date = fields.Date.from_string(contract_obj.joined_date)
#         end_date = fields.Date.from_string(self.last_working_day)
#         print("sub", end_date -start_date)
#         difference = relativedelta(end_date, start_date)
#         difference_years = difference.years + difference.months/12.0 + difference.days/365.0
#         print(difference_years)
#         self.total_employee_duration = "{:d} Years  {:d} Months {:d} Days".format(difference.years , difference.months,difference.days)
#         print("new amount")
#         if self.type == "Resignation":
#             print("IN" ,difference_years)
#             if difference_years < 2:
#                 self.eos_amount = "NO EOS Amount"
#             elif difference_years >= 2 and difference_years <= 5:
#                 self.eos_amount = difference.years*contract_obj.wage / 6
#                 print(self.eos_amount)
#             elif difference_years > 5 and difference_years < 10:
#                 self.eos_amount = ((5*contract_obj.wage /2) + (contract_obj.wage *(difference_years-5)))* 2/3
#                 print(self.eos_amount)
#             elif difference.years >= 10:
#                 self.eos_amount  = (5*contract_obj.wage /2) + (contract_obj.wage * (difference_years-5))
#                 print(self.eos_amount)
#         elif self.type == "Termination":
#             if difference_years < 5 :
#                 self.eos_amount = difference_years * contract_obj.wage * 0.5
#                 print(self.eos_amount)
#             elif difference_years >= 5:
#                 self.eos_amount  = (5*contract_obj.wage /2) + (contract_obj.wage * (difference_years-5))
#                 print(self.eos_amount)
