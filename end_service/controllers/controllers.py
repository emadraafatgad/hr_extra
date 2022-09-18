# -*- coding: utf-8 -*-
from odoo import http

# class EndService(http.Controller):
#     @http.route('/end_service/end_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/end_service/end_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('end_service.listing', {
#             'root': '/end_service/end_service',
#             'objects': http.request.env['end_service.end_service'].search([]),
#         })

#     @http.route('/end_service/end_service/objects/<model("end_service.end_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('end_service.object', {
#             'object': obj
#         })