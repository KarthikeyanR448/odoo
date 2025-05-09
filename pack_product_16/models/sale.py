from odoo import models, fields, api, _


pack_dragged = False

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_sequence = fields.Integer(compute="get_line_sequence")
    sub_product_compute = fields.Integer(compute="compute_sub_product", store=True)


    @api.depends('order_line')
    def compute_sub_product(self):
        global pack_dragged
        for rec in self:
            current_pack = self.env['sale.order.line']
            if not pack_dragged:
                line_list = rec.order_line._origin.ids
                if line_list:
                    for line in rec.order_line.sorted('sequence'):
                        if line.is_pack:
                            current_pack = line
                        if not line.is_pack and not line.display_type:
                            line.pack_line_id = current_pack

                    for sub in rec.order_line.filtered(lambda l: l.is_pack):
                        sub.subproduct_line_ids = rec.order_line.filtered(lambda l: l.pack_line_id == sub).ids

            if pack_dragged:
                order_lines = rec.order_line
                pack_ids = order_lines.filtered(lambda x: x.is_pack or x.display_type)
                all_sequences = sorted(order_lines.mapped('sequence'))
                if all_sequences:
                    drag_sequence = all_sequences[0]
                    lines_to_update = []
                    for pack in pack_ids.sorted('sequence'):
                        if pack.is_pack or pack.display_type:
                            lines_to_update.append((1, pack._origin.id, {'sequence': drag_sequence}))
                            if pack.is_pack:
                                for subproduct in pack.subproduct_line_ids:
                                    drag_sequence += 1
                                    lines_to_update.append((1, subproduct._origin.id, {'sequence': drag_sequence}))
                        drag_sequence += 1
                    if lines_to_update:
                        rec.write({'order_line': lines_to_update})
                pack_dragged = False

            rec.sub_product_compute = 0


    @api.depends('order_line')
    def get_line_sequence(self):
        if self.order_line:
            for line in self.order_line:
                self.product_sequence = line.sequence
        else:
            self.product_sequence = 0


    def get_current_line(self, className):
        """
            Function called from js rpc to find pack_product or sub_product is dragged
        """
        global pack_dragged
        if "o_is_pack" in className:
            pack_dragged = True
        else:
            pack_dragged = False



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_pack = fields.Boolean(string="Is pack", related="product_id.is_pack")
    changed_quantity = fields.Float(string="Old Quantity")
    parent_pack_prod = fields.Many2one('product.product', domain=[('is_pack', '=', True)], 
                                       help='This field is used to Determine Parent pack product')
    subproduct_line_ids = fields.Many2many('sale.order.line','sale_order_line_subproduct_rel','order_line_id','subproduct_line_id',
                                           store=True,copy=False)
    pack_line_id = fields.Many2one('sale.order.line',store=True,copy=False)

    hide_product = fields.Boolean(readonly=True)
    pack_closed = fields.Boolean(readonly=True, default=False)

    def sub_product_btn(self):
        if not self.pack_closed:
            self.pack_closed = True
            for rec in self.subproduct_line_ids:
                rec.hide_product = True
        else:
            self.pack_closed = False
            for rec in self.subproduct_line_ids:
                rec.hide_product = False





