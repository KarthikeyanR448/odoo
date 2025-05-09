from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SelectPack(models.TransientModel):
    _name = 'select.product.pack'
    _rec_name = 'product_id'
    _description = 'Add product pack to sale order'

    product_id = fields.Many2one('product.product', string='Select Pack', 
                                 domain=[('is_pack', '=', True)], required=True)
    quantity = fields.Float('Quantity', default=1, required=True)
    sale_or_template = fields.Integer()
    form_model = fields.Char()




    def add_pack_order(self):
        if self.sale_or_template and self.form_model == 'sale.order':
            sale_id = self.env['sale.order'].browse(self.sale_or_template)
            name = ''
            if self.product_id.description_sale:
                name = self.product_id.description_sale
            if self.product_id.is_pack:
                unitprice = 0
                for rec in self.product_id.pack_products_ids:
                    unitprice = unitprice + (rec.qty * rec.price)
                sequence = sale_id.product_sequence + 1
                sub_product = self.env['sale.order.line']
                pack_product = self.env['sale.order.line'].create({
                    'sequence': sequence,
                    'product_id': self.product_id.id,
                    'price_unit': unitprice,
                    'product_uom': self.product_id.uom_id.id,
                    'product_uom_qty': self.quantity,
                    'order_id': sale_id.id,
                    'name': name,
                    'price_subtotal': unitprice,
                    'tax_id': self.product_id.taxes_id.ids
                })
                for rec in self.product_id.pack_products_ids:
                    sequence = sequence + 1
                    description = ''
                    if rec.product_id.description_sale:
                        description = rec.product_id.description_sale 
                    sub_product += self.env['sale.order.line'].create({
                        'sequence': sequence,
                        'product_id': rec.product_id.id,
                        'price_unit': rec.product_id.lst_price,
                        'product_uom': rec.product_id.uom_id.id,
                        'pack_line_id': pack_product.id,
                        'product_uom_qty': rec.qty,
                        'order_id': sale_id.id,
                        'name': description,
                        'tax_id': self.product_id.taxes_id.ids
                    })
                sale_id.product_sequence = sequence
                pack_product.subproduct_line_ids = sub_product

    @api.constrains('quantity')
    def _check_positive_qty(self):
        if any([ml.quantity < 0 for ml in self]):
            raise ValidationError(_('You cannot enter negative quantities.'))
