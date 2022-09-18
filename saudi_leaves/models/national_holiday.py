# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _, SUPERUSER_ID
from datetime import datetime



class national_holiday(models.Model):
    _name = "hr.national.holiday"
    _inherit = "mail.thread"

    name = fields.Char('Description')
    year = fields.Integer(string="Year")
    start_date = fields.Date(string="Holiday Start Date")
    end_date = fields.Date(string="Holiday End Date")
    duration = fields.Integer(string="Holiday Duration" , compute="_compute_duration")
    state = fields.Selection([
        ('New', 'New'),
        ('Confirmed', 'Confirmed'),
    ], string='Status', select=True, default='New', )




    @api.constrains('year')
    def _check_year(self):
        if self.year < 0:
            raise exceptions.ValidationError(
                _("Year Can not be minus‬‬"))
        if self.year <= 2010 or self.year >= 2100:
            raise exceptions.ValidationError(" Data Error!! \n Year range must be greater than 2010 and less than 2100")

    @api.depends('start_date','end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                start_date = datetime.strptime(rec.start_date, "%Y-%m-%d")
                end_date = datetime.strptime(rec.end_date, "%Y-%m-%d")
                timedelta = end_date - start_date
                rec.duration = timedelta.days + 1


    @api.multi
    def send_mail_to_employee(self):
        for record in self:
            raise exceptions.ValidationError("Under development.")
        return {}

    @api.constrains('end_date')
    def _check_end_date(self):
        if self.end_date < self.start_date:
            raise exceptions.ValidationError(" Data Error!! \n Holiday end date must be greater than holiday start date !")


    @api.multi
    def action_confirm(self):
        for record in self:
            old_holidays = self.env['hr.national.holiday'].search([])
            for old_holiday in old_holidays:
                if old_holiday.end_date < record.start_date or old_holiday.start_date > record.end_date:
                    continue
                elif old_holiday.id == record.id:
                    continue
                else:
                    raise exceptions.ValidationError(" Data Error!! \n This Holiday conflicts with another Holiday.")
            record.write({'state': 'Confirmed'})
            body = "This Record Confirmed"
            self.message_post(body=body, message_type='email')
        return {}

    @api.multi
    def action_set_new(self):
        for record in self:
            record.write({'state': 'New'})
            body = "This Record Set To New"
            self.message_post(body=body, message_type='email')
        return {}