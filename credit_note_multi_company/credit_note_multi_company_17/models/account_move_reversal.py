from odoo import models, fields, api, Command, _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'


    account_move_reversal_line = fields.One2many('account.move.reversal.line', 'refund_id')

    def select_all_product(self):
        for line in self.account_move_reversal_line:
            line.select_product = True
        return {
            'view_mode': 'form',
            'res_model': 'account.move.reversal',
            'res_id': self.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    @api.model
    def default_get(self,fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        product_list = []
        if active_model == 'account.move' and active_id:
            account_move = self.env[active_model].browse([active_id])
            invoice_line_ids = account_move.invoice_line_ids
            for move_line in invoice_line_ids:
                line_data = {
                    'product_id': move_line.product_id.id,
                    'quantity': move_line.quantity,
                    'uom_id': move_line.product_uom_id.id,
                    'price_unit': move_line.price_unit,
                    'move_line_id': move_line.id,
                    }
                if move_line.product_id.type == 'service': #refund_percent 100 by default for service products
                    line_data.update({'refund_percent': 100})
                product_list.append((0, 0, line_data))
            res.update({'account_move_reversal_line': product_list})
        return res
    
    def _prepare_default_reversal(self, move):
        defaults = super()._prepare_default_reversal(move)
        account_move_reversal_line = self.account_move_reversal_line.filtered(lambda refund_product: refund_product.select_product)
        defaults['line_ids'] = []
        defaults['ref'] = move.ref
        for refund_line in account_move_reversal_line:
            defaults['line_ids'].append(Command.create({
                'product_id': refund_line.product_id.id,
                'quantity': refund_line.quantity,
                'account_id': refund_line.account_id.id,
                'price_unit': (refund_line.price_unit/100)*refund_line.refund_percent,
                'credit_reason_id': refund_line.reason_id.id,
                'tax_ids': refund_line.move_line_id.tax_ids.ids,
            }))
        return defaults

class AccountMoveReversalLine(models.TransientModel):
    _name = 'account.move.reversal.line'
    _description = 'Account Move Reversal Line'

    refund_id = fields.Many2one('account.move.reversal')
    move_line_id = fields.Many2one('account.move.line', 'Account move line')
    product_id = fields.Many2one('product.product', string='Product Name')
    account_id = fields.Many2one('account.account', related='move_line_id.account_id')
    quantity = fields.Float(string="Quantity")
    price_unit = fields.Float(string='Unit Price')
    select_product = fields.Boolean(string=' ')
    reason_id = fields.Many2one('account.refund.reason', string='Reason')
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    refund_percent = fields.Float(string='Refund Percentage (%)')

    @api.onchange('reason_id')
    def onchange_reason_id(self):
        """change the refund percent"""
        for rec in self:
            if rec.reason_id:
                rec.refund_percent = rec.reason_id.refund_percent
