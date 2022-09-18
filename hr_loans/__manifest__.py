# -*- coding: utf-8 -*-
{
    'name': "Hr Loans",
    'summary': ' Hr Loans',
    'description': " Hr Loans ",
    'author': "OserGroup",
    'website': "",
    'category': 'Saudi HR',
    'version': '0.1',
    'depends': [
        'mail',
        'base',
        'saudi_hr_employee',
        'saudi_hr_contract',
        'saudi_hr_payroll',
        # 'saudi_hr_leaves',
        'basic_hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_loans.xml',
        'views/hr_rewards.xml',
        'views/request_sequence.xml',
        'views/salary_structure_data.xml',
        'res_config_view.xml',
    ],
}