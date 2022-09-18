# -*- coding: utf-8 -*-

# class HrAccounts(http.Controller):
#     @http.route('/hr_accounts/hr_accounts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_accounts/hr_accounts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_accounts.listing', {
#             'root': '/hr_accounts/hr_accounts',
#             'objects': http.request.env['hr_accounts.hr_accounts'].search([]),
#         })

#     @http.route('/hr_accounts/hr_accounts/objects/<model("hr_accounts.hr_accounts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_accounts.object', {
#             'object': obj
#         })
