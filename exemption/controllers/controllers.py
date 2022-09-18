# -*- coding: utf-8 -*-

# class Exemption(http.Controller):
#     @http.route('/exemption/exemption/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/exemption/exemption/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('exemption.listing', {
#             'root': '/exemption/exemption',
#             'objects': http.request.env['exemption.exemption'].search([]),
#         })

#     @http.route('/exemption/exemption/objects/<model("exemption.exemption"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('exemption.object', {
#             'object': obj
#         })
