# -*- coding: utf-8 -*-
from odoo import models, fields, _


class HrEmployeeEdit(models.Model):
    _inherit = 'hr.employee'

    id_release_date = fields.Date('Release Date')
    id_ex_date = fields.Date('Expiry Date')
    passport_release_date = fields.Date('Release Date')
    passport_ex_date = fields.Date('Expiry Date')


class HrEmployeeFamily(models.Model):
    _inherit = 'hr.employee.family'

    arbic_name = fields.Char('Arabic Name')
    member_id = fields.Char('ID')
    birth_date = fields.Date('Birth Date')


class HrEmergencyContact(models.Model):
    _inherit = 'hr.emergency.contact'

    rel = fields.Char('Relationship')


class HrContractEdit(models.Model):
    _inherit = 'hr.contract'

    type = fields.Selection([('saudi', 'Saudi'),
        ('foreigner', 'Foreigner')], string='Type', default='saudi')
