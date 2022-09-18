# -*- coding: utf-8 -*-
{
    'name': "exemption core",

    'summary': """
            Handle employee permissions included (Late sign in, Early sign out, Other)
        """,

    'description': """
            Handle employee permissions included (Late sign in, Early sign out, Other)
        """,

    'author': "Mahmoud Nayel - MarketME",
    'website': "http://www.marketme-mena.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_requests_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
