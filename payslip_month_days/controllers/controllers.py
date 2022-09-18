# -*- coding: utf-8 -*-

# class PayslibMonthDays(http.Controller):
#     @http.route('/payslip_month_days/payslip_month_days/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payslip_month_days/payslip_month_days/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payslip_month_days.listing', {
#             'root': '/payslip_month_days/payslip_month_days',
#             'objects': http.request.env['payslip_month_days.payslip_month_days'].search([]),
#         })

#     @http.route('/payslip_month_days/payslip_month_days/objects/<model("payslip_month_days.payslip_month_days"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payslip_month_days.object', {
#             'object': obj
#         })
