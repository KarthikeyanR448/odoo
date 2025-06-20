from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"


    @api.model
    def get_existing_lots(self, company_id, product_id):
        """
        Return the lots that are still available in the given company.
        The lot is available if its quantity in the corresponding stock_quant and pos stock location is > 0.
        """
        self.check_access('read')
        pos_config = self.env['pos.config'].browse(self._context.get('config_id'))
        if not pos_config:
            raise UserError(_('No PoS configuration found'))

        src_loc = pos_config.picking_type_id.default_location_src_id
        src_loc_quants = self.sudo().env['stock.quant'].search([
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company_id),
            ('product_id', '=', product_id),
            ('location_id', 'in', src_loc.child_internal_location_ids.ids),
        ])
        available_lots = src_loc_quants.\
            filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=q.product_id.uom_id.rounding) > 0).\
            mapped('lot_id')

        return available_lots.read(['id', 'name', 'product_qty', 'sale_price', 'currency_symbol'])
    
class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def _load_pos_data_models(self, config_id):
        return ['pos.config', 'pos.order', 'pos.order.line', 'pos.pack.operation.lot', 'pos.payment', 'pos.payment.method', 'pos.printer',
                        'pos.category', 'pos.bill', 'res.company', 'account.tax', 'account.tax.group', 'product.product', 'product.attribute', 'product.attribute.custom.value',
            'product.template.attribute.line', 'product.template.attribute.value', 'product.combo', 'product.combo.item', 'product.packaging', 'res.users', 'res.partner', 'stock.lot',
            'decimal.precision', 'uom.uom', 'uom.category', 'res.country', 'res.country.state', 'res.lang', 'product.pricelist', 'product.pricelist.item', 'product.category',
            'account.cash.rounding', 'account.fiscal.position', 'account.fiscal.position.tax', 'stock.picking.type', 'res.currency', 'pos.note', 'ir.ui.view', 'product.tag', 'ir.module.module']
