# -*- coding: utf-8 -*-
{
    'name': "Hr Modification",

    'summary': """
        Hr Modification""",

    'description': """
        Hr Modification
    """,

    'author': 'Saad El Wardany - MarketMe (mm_me)',
    'website': 'www.marketme-it.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/emp.xml',
        'views/hr_contract.xml',
    ],
    # only loaded in demonstration mode
}