{
    'name': "Sale Product Pack",

    'summary': """Sale Product Pack""",

    'description': """Sale Product Pack """,

    'author': "",
    'website': "",
    'version': '16.0.0.1',
    'depends': [
        'web',
        'sale',
        'sale_management',
        'product',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/select_product_pack_view.xml',
        'views/sale_order_view.xml',
        'views/product_inherit_view.xml',
    ],

    "assets": {
        "web.assets_backend": [
            "/pack_product/static/src/js/sale_custom.js",
            "/pack_product/static/src/scss/sale_style.css",
        ]
    },


    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

