# -*- coding: utf-8 -*-

# class Exemption(http.Controller):
#     @http.route('/exemption_core/exemption_core/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/exemption_core/exemption_core/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('exemption_core.listing', {
#             'root': '/exemption_core/exemption_core',
#             'objects': http.request.env['exemption.exemption'].search([]),
#         })

#     @http.route('/exemption_core/exemption_core/objects/<model("exemption.exemption"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('exemption_core.object', {
#             'object': obj
#         })
