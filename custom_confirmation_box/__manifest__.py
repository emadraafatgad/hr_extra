# -*- coding: utf-8 -*-
{
    'name': "Confirmation Box",

    'summary': """
        Confirmation Box""",

    'description': """
        Confirmation Box Dialogue
    """,

    'author': "OserGroup",
    'website': "saad.wardany@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Saudi HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/views/confirmation_wizard.xml',
    ],
}