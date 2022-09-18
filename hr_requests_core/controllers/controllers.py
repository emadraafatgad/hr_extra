# -*- coding: utf-8 -*-

# class HrRequests(http.Controller):
#     @http.route('/hr_requests_new_new/hr_requests_new_new/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_requests_new_new/hr_requests_new_new/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_requests_new_new.listing', {
#             'root': '/hr_requests_new_new/hr_requests_new_new',
#             'objects': http.request.env['hr_requests_new_new.hr_requests_new_new'].search([]),
#         })

#     @http.route('/hr_requests_new_new/hr_requests_new_new/objects/<model("hr_requests_new_new.hr_requests_new_new"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_requests_new_new.object', {
#             'object': obj
#         })
