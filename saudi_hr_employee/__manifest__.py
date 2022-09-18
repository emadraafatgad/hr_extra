# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Extend HR Employees',
    'version': '1.1',
    'summary': 'Adding new fields in HR',
    'sequence': 30,
    'description': "",
    'category': 'Saudi HR',
    'author': "",
    'website': "",
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'saudi_hr_recruitment',
        'custom_confirmation_box',
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/hr_seq.xml',
        'views/hr_view.xml',
        'views/departments.xml',
        'views/effective_notice.xml',
        'views/employee_history.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
