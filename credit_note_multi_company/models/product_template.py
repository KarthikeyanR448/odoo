from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_shipping_product = fields.Boolean(
        string="Shipping Product",
        help="This product is used for shipping purposes.",    
    )
