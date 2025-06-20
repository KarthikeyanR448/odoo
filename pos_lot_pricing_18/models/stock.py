from odoo import _, api, fields, models
from odoo.exceptions import UserError

class StockMoveLineCreate:
    
    def __init__(self, record, move, picking_id):
        self.record = record
        self.env = record.env
        self.move = move
        self.picking_id = picking_id

    def create_stock_move_line(self):
        if self.picking_id and self.move:
            move_line_vals = []
            pricelist_item_id = [line for line in self.record.product_pricelist_id.item_ids if line.categ_id.id == self.move.product_id.categ_id.id] if self.record.product_pricelist_id.item_ids else False
            pricelist_item_id = pricelist_item_id[0] if pricelist_item_id else False
            move_line_to_update_lot = self.move.move_line_ids.filtered(lambda l: l.move_id.id == self.move.id and l.lot_name)
            if not move_line_to_update_lot:
                lot_name = self.env['ir.sequence'].search([("code", "=", "stock.lot.pricing")]).next_by_id()
            else:
                lot_name = move_line_to_update_lot.lot_name
            if pricelist_item_id and self.move.product_id.categ_id.id == pricelist_item_id.categ_id.id:
                move_line_vals = {
                    "lot_name": lot_name,
                    "move_id": self.move.id,
                    "product_id": self.move.product_id.id,
                    "origin": self.picking_id.origin,
                    "quantity": self.move.product_uom_qty,
                    "reference": self.picking_id.name,
                    "cost_price": self.move.purchase_line_id.price_unit,
                    "margin_percent": pricelist_item_id.price_markup,
                }
            if move_line_vals:
                move_line_to_update = self.move.move_line_ids.filtered(lambda l: l.move_id.id == self.move.id)
                if move_line_to_update:
                    move_line_to_update.update(move_line_vals)
                else:
                    self.picking_id.move_line_ids.create(move_line_vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_pricelist_id = fields.Many2one("product.pricelist", string="Product Pricelist")

    def calculate_price(self):
        for move in self:
            picking_id = move.picking_id
            move_line_creation = StockMoveLineCreate(self, move, picking_id)
            move_line_creation.create_stock_move_line()
    
    def _create_production_lots_for_pos_order(self, lines):
        ''' Search for existing lots and create missing ones.

            :param lines: pos order lines with pack lot ids.
            :type lines: pos.order.line recordset.

            :return stock.lot recordset.
        '''
        valid_lots = self.env['stock.lot']
        moves = self.filtered(lambda m: m.picking_type_id.use_existing_lots)
        # Already called in self._action_confirm() but just to be safe when coming from _launch_stock_rule_from_pos_order_lines.
        self._check_company()
        if moves:
            moves_product_ids = set(moves.mapped('product_id').ids)
            lots = lines.pack_lot_ids.filtered(lambda l: l.lot_name and l.product_id.id in moves_product_ids)
            lot_sequence = self.env['ir.sequence'].search([("code", "=", "stock.lot.pricing")])
            if lots and lot_sequence:
                for lot in lots:
                    lot['lot_name'] = lot['lot_name'][:lot_sequence.padding+1]
            lots_data = set(lots.mapped(lambda l: (l.product_id.id, l.lot_name)))
            existing_lots = self.env['stock.lot'].search([
                '|', ('company_id', '=', False), ('company_id', '=', moves[0].picking_type_id.company_id.id),
                ('product_id', 'in', lines.product_id.ids),
                ('name', 'in', lots.mapped('lot_name')),
            ])
            #The previous search may return (product_id.id, lot_name) combinations that have no matching in lines.pack_lot_ids.
            for lot in existing_lots:
                if (lot.product_id.id, lot.name) in lots_data:
                    valid_lots |= lot
                    lots_data.remove((lot.product_id.id, lot.name))
            moves = moves.filtered(lambda m: m.picking_type_id.use_create_lots)
            if moves:
                moves_product_ids = set(moves.mapped('product_id').ids)
                missing_lot_values = []
                for lot_product_id, lot_name in filter(lambda l: l[0] in moves_product_ids, lots_data):
                    missing_lot_values.append({'company_id': self.company_id.id, 'product_id': lot_product_id, 'name': lot_name})
                valid_lots |= self.env['stock.lot'].create(missing_lot_values)
        return valid_lots


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    cost_price = fields.Float(string='Cost Price')
    margin_percent = fields.Float(string='Margin(%)')
    sale_price = fields.Float(string='Sale Price', compute="_compute_sale_price")

    @api.depends('cost_price','margin_percent')
    def _compute_sale_price(self):
        for line in self:
            if line.cost_price and line.margin_percent:
                line.sale_price = line.cost_price + (line.cost_price * line.margin_percent)/100
            else:
                line.sale_price = 0

    @api.onchange('margin_percent')
    def _check_margin_percent(self):
        for line in self:
            if line.margin_percent and (line.margin_percent < 1 or line.margin_percent >100):
                raise UserError(_("Margin percent cannot be less than 1 or greater than 100"))

    def _prepare_new_lot_vals(self):
        res = super(StockMoveLine, self)._prepare_new_lot_vals()
        res.update({
            'sale_price': self.sale_price,
            'company_id': self.env.company.id,
        })
        return res

class StockLot(models.Model):
    _inherit = 'stock.lot'

    sale_price = fields.Float(string='Sale Price', readonly=True)
    currency_symbol = fields.Char(related="company_id.currency_id.symbol")

    def get_lot_values(self, values):
        lot_sequence = self.env['ir.sequence'].search([("code", "=", "stock.lot.pricing")])
        if values and lot_sequence:
            if isinstance(values, list):
                lot_name = values[0][1]['lot_name'][:lot_sequence.padding+1]
            if isinstance(values, str):
                lot_name = values
            lot_id = self.env['stock.lot'].search([("name", "=", lot_name)])
            return {
                'lot_name': lot_id.name, 
                'quantity': lot_id.product_qty, 
                'sale_price': lot_id.sale_price
            }
        
    def _load_pos_data_domain(self):
        return []
    
    def _load_pos_data_fields(self):
        return ['id', 'name', 'product_id']
    
    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain()
        fields = self._load_pos_data_fields()
        return {
            'data': self.search_read(domain, fields, load=False),
            'fields': self._load_pos_data_fields(),
        }
