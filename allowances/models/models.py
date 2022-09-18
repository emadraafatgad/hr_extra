# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class payslip_run(models.Model):
    _inherit = 'hr.payslip.run'

    def confirm_all(self):
        if not self.slip_ids:
            raise UserError("there is no payslip generated to confirm")
        for slip in self.slip_ids:
            slip.compute_sheet()
            slip.action_payslip_done()


class project(models.Model):
    _inherit = 'hr.expense'

    @api.multi
    def submit_expenses(self):
        if any(expense.state != 'draft' for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report!"))
        sheet = self.env['hr.expense.sheet'].create({
            'expense_line_ids': [(6, 0, [line.id for line in self])],
            'employee_id': self[0].employee_id.id,
            'name': self[0].name if len(self.ids) == 1 else ''
        })
        self.view_sheet()
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'hr.expense.sheet',
        #     'target': 'current',
        #     'domain': [('id', '=', sheet.id)]
        #     # 'context': {
        #     #     'default_expense_line_ids': [line.id for line in self],
        #     #     'default_employee_id': self[0].employee_id.id,
        #     #     'default_name': self[0].name if len(self.ids) == 1 else ''
        #     # }
        # }


class project(models.Model):
    _inherit = 'hr.contract'
    # val = fields.Integer(string='Val')

    houseallowance = fields.Float(string='House Allowance', help="monthly house allowance.")
    transallowance = fields.Float(string='Transportation Allowance', help="monthly transportation allowance.")
    phoneallowance = fields.Float(string='Phone Allowance', help="monthly phone allowance.")
    otherallowances = fields.Float(string='Other Allowances', help="monthly other allowances .")
    bankfees = fields.Float(string='Bank Fees', help="monthly bank fees .")
    nationality = fields.Boolean(string='Is a Saudi', required=True)
    gosi = fields.Float(string='Gosi', help="Gosi.")
    employee_gosi = fields.Float(string='Employee GOSI', help="Employee Gosi.")
    company_gosi = fields.Float(string='Company Gosi', help="Company Gosi.")
    otherdeducions = fields.Float(string='Other Deductions', help="Other deductions.")
    foodallowance = fields.Float(string='Food Allowance', help="Food Allowance.")
    hasvacationeach = fields.Float(string='Has Vacation Each', help="annual vacation.")
    annualvacation = fields.Float(string='Annual Vacation Period', help="annual vacation period.")
    hasticketseach = fields.Float(string='Has Tickets Each', help="Tickets.")
    no_tickets = fields.Float(string='No of Tickets', help="No Of tickets.")
    vac_balance = fields.Float("Vacation balance")
    done_vac = fields.Float("Done Vacations", default=0.0)

    @api.onchange('annualvacation', 'hasvacationeach', 'date_end', 'date_start')
    def _update_vac_balance(self):
        if self.date_start and self.date_end:
            dfrom = fields.Datetime.from_string(self.date_start)
            dto = fields.Datetime.from_string(self.date_end)
            difference_day = relativedelta(dto, dfrom)
            cont_per = (12 * difference_day.years) + difference_day.months
            if self.hasvacationeach:
                self.vac_balance = (cont_per / self.hasvacationeach) * self.annualvacation
        else:
            self.vac_balance = self.annualvacation

    @api.onchange('wage')
    def _compute_allow(self):
        self.houseallowance = self.wage * 0.25
        self.transallowance = self.wage * 0.1

    @api.multi
    # @api.one
    @api.onchange('wage', 'nationality')
    def emp_gosi(self):
        if self.wage:
            if self.nationality == True:
                self.employee_gosi = (10.0 / 100.0) * (self.wage + self.houseallowance)
        else:
            self.employee_gosi = 0.0

    @api.multi
    # @api.one
    @api.onchange('wage', 'nationality')
    def com_gosi(self):
        if self.wage:
            if self.nationality == True:
                self.company_gosi = (12.0 / 100.0) * (self.wage + self.houseallowance)
        else:
            self.company_gosi = 0.0

    @api.multi
    # @api.one
    @api.onchange('wage', 'nationality')
    def _gosi(self):
        if self.wage:
            if self.nationality == True:
                self.gosi = (22.0 / 100.0) * (self.wage + self.houseallowance)
        else:
            self.gosi = 0.0
