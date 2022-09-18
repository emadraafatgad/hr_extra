# -*- coding: utf-8 -*-

# class HrRequests(http.Controller):
#     @http.route('/hr_requests/hr_requests/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_requests/hr_requests/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_requests.listing', {
#             'root': '/hr_requests/hr_requests',
#             'objects': http.request.env['hr_requests.hr_requests'].search([]),
#         })

#     @http.route('/hr_requests/hr_requests/objects/<model("hr_requests.hr_requests"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_requests.object', {
#             'object': obj
#         })
