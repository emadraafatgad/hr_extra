# Api V7 Imports
import odoo
from odoo import SUPERUSER_ID
from odoo import tools
from odoo.modules.module import get_module_resource
from odoo import fields, models, api
from odoo.tools.translate import _


class AccountAccount(models.Model):
    _inherit = "account.account"

    parents = fields.Char(compute='get_parents', string='Parents ids')

    @api.multi
    def get_parents(self):
        for rec in self:
            ids = ''
            account = rec
            while account.parent_id.id:
                ids += str(account.parent_id.id) + ';'
                account = account.parent_id
            self.parents = ids

    @api.multi
    def _get_childs(self):
        res = []
        account = self
        childes = self.search([('parent_id', '=', account.id)])
        while childes:
            res.append(childes.ids)
            for ch in childes:
                res += ch._get_childs()
        return res

    @api.multi
    def get_childs(self):
        self._get_childs()
