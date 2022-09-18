from odoo import fields, api, models


class HrEmployeeTravel(models.Model):
    _inherit = 'hr.contract'
    air_tickets_provided = fields.Integer(string="Air Tickets provided")
    employee_travel_ids = fields.One2many("hr.travel.line", 'contract_id', readonly=True)


class HrTravelLine(models.Model):
    _name = "hr.travel.line"

    name = fields.Char(help='Description for travel')
    contract_id = fields.Many2one('hr.contract')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    travel_purpose = fields.Selection([('vacation', 'Vacation'),
                                       ('business', 'Business'),
                                       ('conference', 'Conference')], string="Traveling Purpose")
    travel_date_from = fields.Date()
    travel_date_to = fields.Date()
    air_line = fields.Many2one('air.line')
    exit_re_entry_issued = fields.Selection([('yes', 'Yes'), ('no', 'NO')])
    travel_ticket_issued = fields.Integer()
    travel_ticket_remaining = fields.Integer(readonly=True, store=True)

    @api.onchange('travel_ticket_issued', 'contract_id')
    def calc_ticket_remaining(self):
        self.calc_ticket()

    def calc_ticket(self):
        contract_obj = self.env['hr.contract'].search([('id', '=', self.contract_id.id)])
        print(contract_obj.name, "contract")
        travel_line_objs = self.env['hr.travel.line'].search([])
        print(travel_line_objs, "+++++")
        sum = 0
        for line in travel_line_objs:
            sum = sum + line.travel_ticket_issued
        print(sum, "=====")
        print(contract_obj.air_tickets_provided)

        if contract_obj.air_tickets_provided:
            self.travel_ticket_remaining = contract_obj.air_tickets_provided - sum - self.travel_ticket_issued
            print(self.travel_ticket_remaining, "time remaining")

    @api.model
    def create(self, vals):
        contract_obj = self.env['hr.contract'].search([('id', '=', vals['contract_id'])])
        travel_line_objs = self.env['hr.travel.line'].search([])
        print(travel_line_objs, "+++++")
        sum = 0
        for line in travel_line_objs:
            sum = sum + line.travel_ticket_issued
        print(sum, "=====")
        print(contract_obj.air_tickets_provided)
        if contract_obj.air_tickets_provided:
            ticket_remaining = contract_obj.air_tickets_provided - sum - vals['travel_ticket_issued']
            print(ticket_remaining, 'remaining')
            vals['travel_ticket_remaining'] = ticket_remaining
        return super(HrTravelLine, self).create(vals)


class AirLine(models.Model):
    _name = "air.line"
    name = fields.Char("Name")
