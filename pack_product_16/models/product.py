from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductInherit(models.Model):
    _inherit = 'product.template'

    def default_pack_location(self):
        company_user = self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit = 1)
        if warehouse:
            return warehouse.lot_stock_id.id

    is_pack = fields.Boolean("Is Pack")
    pack_location_id = fields.Many2one('stock.location', domain=[('usage', 'in', ['internal', 'transit'])],
                                       default=default_pack_location)
    pack_prices = fields.Float(string="Pack Price", compute='_set_pack_price', store=True)
    pack_products_ids = fields.One2many('pack.products', 'product_tmpl_id', string='Pack Products', copy=True)

    @api.depends('pack_products_ids', 'pack_products_ids.price')
    def _set_pack_price(self):
        price = 0
        for record in self:
            for line in record.pack_products_ids:
                price = price + (line.qty * line.price)
            record.pack_prices = price

class PackProducts(models.Model):
    _name = 'pack.products'
    _rec_name = 'product_tmpl_id'
    _description = 'Select Pack Products'

    product_id = fields.Many2one('product.product', string = 'Product', required = True,
                                 domain = [('is_pack', '=', False)])
    product_tmpl_id = fields.Many2one('product.template', string = 'Product Template')
    price = fields.Float('Price', related="product_id.lst_price", readonly=False)
    qty = fields.Float('Quantity', default = 1)
    qty_available = fields.Float('Quantity Available', compute = 'compute_quantity_of_product', store = True, readonly = False)
    total_available_quantity = fields.Float('Total Quantity')
    uom = fields.Char(string="UoM", related="product_id.uom_id.name")
    price_subtotal = fields.Float(string="Subtotal", compute ="_compute_price_subtotal")

    @api.depends('price','qty')
    def _compute_price_subtotal(self):
        for rec in self:
            if rec.price and rec.qty:
                rec.price_subtotal = rec.price * rec.qty
            else:
                rec.price_subtotal = 0

    @api.depends('product_id', 'total_available_quantity', 'product_id.qty_available')
    def compute_quantity_of_product(self):
        for record in self:
            location_id = record.product_tmpl_id.pack_location_id
            if location_id:
                stock_quant = self.env['stock.quant'].search([
                    ('product_id','=',record.product_id.id),
                    ('location_id','=',location_id.id)
                    ])
                if stock_quant:
                    record.qty_available = stock_quant.quantity
                else:
                    record.qty_available = False
            else:
                record.qty_available = False

    @api.constrains('qty')
    def _check_positive_qty(self):
        if any([ml.qty < 0 for ml in self]):
            raise ValidationError(_('You can not enter negative quantities.'))

