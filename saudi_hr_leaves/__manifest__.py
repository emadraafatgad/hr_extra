# -*- coding: utf-8 -*-
{
    'name': "Saudi HR Leaves",
    'summary': 'Saudi HR Leaves',
    'description': 'Saudi HR Leaves',
    'author': "OserGroup",
    'website': "",
    'category': 'Saudi HR',
    'version': '0.1',
    'depends': [
        'hr_holidays',
        'saudi_hr_employee',
        'saudi_hr_contract',
        'basic_hr',
        'hr_holidays',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/leave_request.xml',
        'views/menus.xml',
        'views/hr_leaves.xml',
        'views/leave_reconciliation.xml',
        'views/national_holiday.xml',
        'views/leave_allocation.xml',
        'views/air_tickets.xml',
        'wizard/batch_generate_requests.xml',
    ],
}