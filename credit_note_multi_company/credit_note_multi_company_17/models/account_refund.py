from odoo import models, fields, api, _


class AccountRefundReason(models.Model):
    _name = 'account.refund.reason'
    _description = 'Refund reason for credit notes'
    _rec_name = 'reason'

    reason = fields.Char(string="Reason")
    refund_percent = fields.Float(string="Refund Percentage")

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    credit_reason_id = fields.Many2one('account.refund.reason',string="Reason")
