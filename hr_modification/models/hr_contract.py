# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrSalaryScale(models.Model):
    _name = "hr.salary.scale"
    _inherit = "mail.thread"
    _description = "Salary Scale"

    name = fields.Char('Name')
    wage = fields.Float('Basic Salary')
    house_allowance = fields.Float('House Allowance')
    transportation_allowance = fields.Float('Transportation Allowance')


class HrContract(models.Model):
    _inherit = "hr.contract"

    salary_scale_id = fields.Many2one('hr.salary.scale','Salary Scale')
    has_house_allowance = fields.Boolean('Has House Allowance')
    house_allowance = fields.Float('House Allowance')
    has_transportation_allowance = fields.Boolean('Has Transportation Allowance')
    transportation_allowance = fields.Float('Transportation Allowance')
    gosi_employee = fields.Float('Employee GOSI',compute='_compute_gosi_employee')
    gosi_company = fields.Float('Company GOSI')
    bank_fees = fields.Float('Bank Fees')


    @api.depends('wage')
    def _compute_gosi_employee(self):
        for rec in self:
            rec.gosi_employee = rec.wage * 0.1