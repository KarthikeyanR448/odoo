{
    'name' : 'Credit Note - Multi Company Reflection',
    'version': '17.0.1.0',
    'author': 'learning',
    'category': 'Account',
    'website': '',
    'summary': 'Credit Note - Multi Company Reflection',
    'description': '''
    This module enables seamless management and reflection of credit notes across multiple companies in a multi-company environment. 
    It ensures accurate synchronization of credit note records, enhancing financial operations and reporting for businesses operating 
    with multiple entities. The module integrates with core Odoo apps like Sales, Accounting, and Web for a comprehensive solution.
    ''',
   
   'depends': [
        'mail',
        'base',
        'sale',
        'sale_management',
        'account',
        'account_accountant',
        'web',
    ],
    
    'data': [
        'security/ir.model.access.csv',
        'view/account_move.xml',
        'view/account_move_reversal.xml',
        'view/account_refund_reason.xml',
        'view/product_template.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
