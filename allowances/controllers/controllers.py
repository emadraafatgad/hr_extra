# -*- coding: utf-8 -*-

# class Project(http.Controller):
#     @http.route('/project/project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project/project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project.listing', {
#             'root': '/project/project',
#             'objects': http.request.env['project.project'].search([]),
#         })

#     @http.route('/project/project/objects/<model("project.project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project.object', {
#             'object': obj
#         })
