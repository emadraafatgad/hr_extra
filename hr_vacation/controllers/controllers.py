# -*- coding: utf-8 -*-

# class HrVacation(http.Controller):
#     @http.route('/hr_vacation/hr_vacation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_vacation/hr_vacation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_vacation.listing', {
#             'root': '/hr_vacation/hr_vacation',
#             'objects': http.request.env['hr_vacation.hr_vacation'].search([]),
#         })

#     @http.route('/hr_vacation/hr_vacation/objects/<model("hr_vacation.hr_vacation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_vacation.object', {
#             'object': obj
#         })
