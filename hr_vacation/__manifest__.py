# -*- coding: utf-8 -*-
{
    'name': "HR Vacation",

    'summary': """
        Manage annual vacations""",

    'description': """
         Manage annual vacations
    """,

    'author': "MarketMe - Mahmoud Nayel",
    'website': "http://marketme-mena.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr_attendance', 'allowances', 'hr_holidays', 'hr', 'hr_accounts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
