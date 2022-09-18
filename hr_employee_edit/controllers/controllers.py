# -*- coding: utf-8 -*-
from odoo import http

# class HrEmployeeEdit(http.Controller):
#     @http.route('/hr_employee_edit/hr_employee_edit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_employee_edit/hr_employee_edit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_employee_edit.listing', {
#             'root': '/hr_employee_edit/hr_employee_edit',
#             'objects': http.request.env['hr_employee_edit.hr_employee_edit'].search([]),
#         })

#     @http.route('/hr_employee_edit/hr_employee_edit/objects/<model("hr_employee_edit.hr_employee_edit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_employee_edit.object', {
#             'object': obj
#         })