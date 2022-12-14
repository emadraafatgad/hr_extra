# -*- coding: utf-8 -*-
{
    'name': "Overtime Late",
    'summary': """ Overtime Late""",
    'description': """Overtime Late""",
    'author': "OserGroup",
    'website': "",
    'category': 'Saudi HR',
    'version': '0.1',
    'depends': [
        'base',
        'hr_attendance',
        'resource',
        'saudi_hr_employee',
        'saudi_hr_payroll',
        'report_xlsx',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/attendance.xml',
        'views/salary_struct.xml',
        'views/sheet_report.xml',
        'views/sequence.xml',
        'views/working_day_wizard.xml',
        'views/change_workinghours.xml',
        'reports/reports.xml',
        'reports/atendance_report.xml',
    ],
}