# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import __


class ContractConfig(models.Model):
    _name = "print.contract.config"
    _rec_name = "company_id"

    company_id = fields.Many2one('res.company', 'Company')
    company_name_ar = fields.Char('company name in contract(Arabic')
    company_name_en = fields.Char('company name in contract(English')
    address_ar = fields.Char('company address in contract(Arabic')
    address_en = fields.Char('company address in contract(English')
    represented_ar = fields.Char('company represented  (Arabic')
    represented_en = fields.Char('company represented  (English')


class Contract(models.Model):
    _inherit = "hr.contract"

    print_config_id = fields.Many2one('print.contract.config', 'Print configuration',
                                      default=lambda self: self.company_id.print_config_id.id or False)
    job_name_ar = fields.Char('Job name (Arabic)')
    job_name_en = fields.Char('Job name (English)')
