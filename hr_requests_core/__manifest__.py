# -*- coding: utf-8 -*-
{
    'name': "HR Requests Core",

    'summary': """
        Employee Can Add HR Requests """,

    'description': """
         Employee Can Add HR Requests like:
         
            * Un Renew Contract عدم تجديد العقد
            * Resignation استقالة 
            * Termination إقاللة 
            * Promotion ترقية 
            * Business Trip رحلة عمل 
            * Stop Salary إيقاف الراتب 
            * Release Salary استرجاع الراتب 
            * Letter خطاب 
            * Penalty عقوبة 
    """,

    'author': "MarketMe - Mahmoud Nayel",
    'website': "http://marketme-mena.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr', 'hr_contract', 'allowances', 'end_service', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'security/security.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
