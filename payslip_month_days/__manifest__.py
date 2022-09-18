# -*- coding: utf-8 -*-
{
    'name': "Payslip month days",

    'summary': """
        add computed field for  payslip month days""",

    'description': """
        add computed field for  payslip month days
            """,

    'author': "Mahmoud Nayel - MarketME",
    'website': "http://www.marketme-mena.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
