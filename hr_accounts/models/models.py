# -*- coding: utf-8 -*-

from odoo import models, fields


class hr_accounts(models.Model):
    _name = 'hr.accounts'

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    end_of_service_accrual_acc = fields.Many2one('account.account', string='End of Service Accrual Account',
                                                 company_dependent=True)
    end_of_service_exp_acc = fields.Many2one('account.account', string='End of Service Expense Account',
                                             company_dependent=True)
    vacation_accrual_acc = fields.Many2one('account.account', string='Vacations Accrual Acount', company_dependent=True)
    vacation_exp_acc = fields.Many2one('account.account', string='Vacations Expense Account', company_dependent=True)
    tickets_accrual_acc = fields.Many2one('account.account', string='Tickets Accrual Account', company_dependent=True)
    tickets_exp_acc = fields.Many2one('account.account', string='Tickets Expense Account', company_dependent=True)
    eos_journal_id = fields.Many2one('account.journal', string="EOS Journal")
    vac_journal_id = fields.Many2one('account.journal', string="Vacation Journal")

    _sql_constraints = [
        ('company_unique', 'unique (company_id)',
         'Company must be unique, there is another record related to this company'),
    ]
