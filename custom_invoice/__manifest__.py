# -*- coding: utf-8 -*-
{
    'name': "Custom Invoice",
    'summary': """Custom invoice in English/Arabic format""",
    'author': "SIT & think digital",
    'website': "http://sitco.odoo.com/",
    'category': 'Custom',
    'version': '12.0.1',
 
    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],

    # always loaded
    'data': [
        'views/account_config_setting_view.xml',
        'views/model_view.xml',
        'views/templates.xml',

# reports
        'report/report_invoice.xml',
            ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
