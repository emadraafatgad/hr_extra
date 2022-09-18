# -*- coding: utf-8 -*-


{
    'name': 'HR Saudi Leaves',
    'version': '11.0',
    'category': 'HR',
    'summary': 'HR Saudi Leaves',
    'author': 'Saad El Wardany - MarketMe (mm_me)',
    'company': 'MarketMe',
    'website': 'www.marketme-it.com',
    'depends': ['hr','hr_modification','hr_holidays'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/leave_type.xml',
        'views/hr_leave.xml',
        'views/national_holiday.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
    'qweb': [],
    'license': 'AGPL-3',
}
