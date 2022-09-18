{
    'name': ' Code_HR',
    'version': '1.4',
    'summary': ' basics HR',
    'description': """
         attendance
            attendance sheet 
    """,
    'category': 'Code',
    'website': 'http://www.ERA.sa ',
    'depends': ['account', 'sale', 'purchase', "hr_holidays", "hr_payroll", "hr_attendance", 'hr', 'calendar',
                'resource', 'payslip_month_days'],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/code_sa.xml',
        'views/hr_attendance.xml',
        'views/hr_public_holidays.xml',
        'views/hr_attendance_sheet.xml',
        # 'views/hr_end_of_service.xml',
        # 'views/sales_approval.xml',
        # 'views/hr_employee_travel.xml',
        # 'report/eos_report.xml',
        'report/payslip.xml',
        'wizard/hr_payslip_wizard.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
