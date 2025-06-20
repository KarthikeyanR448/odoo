{
    'name': 'POS LOT Pricing',
    'version': '18.0',
    'category': 'Extra Tools',
    'author': "",
    'website': '',
    'license': '',
    'summary': """
                POS Pricing for Lot products to show the specific sale price for the respective LOT.
                Generate LOT with sale price based on the pricelist configuration.""",
    'depends': [
        'base',
        'mail',
        'point_of_sale',
        'stock',
    ],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'wizard/lot_pricing_wizard.xml',
        'views/stock_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_pricing/static/src/*',
        ],
        'point_of_sale.assets_prod': [
            'pos_pricing/static/src/*',
        ]
    },
    'images': [],
    'installable': True,
    'application': False,
    'qweb': [
    ],
}
