from odoo import fields, models
from ..models.stock import StockMoveLineCreate


class LotPricingWizard(models.TransientModel):
    _name = 'lot.pricing.wizard'

    product_pricelist_id = fields.Many2one("product.pricelist", string="Product Pricelist")

    def generate_lot(self):
        picking_id = self.env["stock.picking"]
        if self._context["active_id"]:
            picking_id = self.env["stock.picking"].browse(self._context["active_id"])
        if picking_id:
            for move in picking_id.move_ids_without_package:
                if move:
                    move_line_creation = StockMoveLineCreate(self, move, picking_id)
                    move_line_creation.create_stock_move_line()
