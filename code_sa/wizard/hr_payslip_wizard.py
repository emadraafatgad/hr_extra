import datetime

import dateutil
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, exceptions


# from IPython.testing import tools


class HrPayslipReport(models.TransientModel):
    _name = 'hr.payslip.report.wizard'

    report_for = [("1", "all"),
                  ("2", "select employee"), ]

    report_for = fields.Selection(report_for, string="Report For", default='1')
    date_from = fields.Date(required=True, string="Date From")
    date_to = fields.Date(required=True, string="Date To")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    period = fields.Integer("period", compute="_compute_period")

    @api.depends('date_to', 'date_from')
    def _compute_period(self):
        if self.date_from and self.date_to:
            date1 = dateutil.parser.parse(self.date_to).date()
            date2 = dateutil.parser.parse(self.date_from).date()
            self.period = relativedelta(date1, date2).days

    @api.onchange('date_from')
    def date_from_change(self):
        if self.date_from:
            date_to = datetime.datetime.strptime(self.date_from, "%Y-%m-%d") + relativedelta(
                months=1) - relativedelta(days=1)
            self.date_to = date_to
            emp_id = self.env['hr.payslip'].search([('employee_id', '=', 1)], limit=1)
            for l in emp_id.line_ids:
                print(l.category_id.name)

    def _make_contexts(self, data):
        result = {}
        result['employee_id'] = 'employee_id' in data['form'] and data['form']['employee_id'] or False
        result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or False
        result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
        return result

    @api.multi
    def make_report(self):
        if self.report_for == '2':
            domain_results = self.env['hr.payslip'].search(
                [('date_from', '=', self.date_from), ('date_to', '=', self.date_to),
                 ('employee_id', 'in', self.employee_ids.ids)])
        else:
            domain_results = self.env['hr.payslip'].search(
                [('date_from', '=', self.date_from), ('date_to', '=', self.date_to), ])

        # print(domain_results.ids, "domain")
        # print domain_results
        # print (len(domain_results), "length")
        if len(domain_results) >= 1:
            data = {}
            data['ids'] = domain_results.ids
            data['model'] = self.env.context.get('active_model', 'hr.payslip')
            # print 'datamodel', data['model']
            data['form'] = self.read(['employee_ids', 'month'])[0]
            # print(data['form']['account_id'][0], 'data form account_id')

            used_context = self._make_contexts(data)
            data['form']['used_context'] = dict(used_context)
            return self._print_report(data)
        else:
            raise exceptions.ValidationError(
                ('Warning! There is no records to print from this search'))

    def _print_report(self, data):
        data['form'].update(self.read(
            ['employee_ids', 'month', ])[0])
        return self.env.ref('code_sa.employee_payslips_report').with_context(landscape=True).report_action(
            self, data=data)


class JournalItemsReport(models.AbstractModel):
    _name = 'report.code_sa.report_employee_payslips_template'

    @api.multi
    def get_report_values(self, docids, data=None):
        self.model = data['model']
        docs = self.env[self.model].browse((data['ids']))
        d_ids = []
        for doc in docs:
            d_ids.append(doc.department_id.id)
        deps = self.env['hr.department'].search([('id', 'in', d_ids)])

        return {
            'doc_ids': data['ids'],
            'doc_model': self.model,
            'docs': docs,
            'deps': deps,
            'data': data['form'],
        }
        # return self.env['report'].render('code_sa.report_employee_payslips_template', docargs)
