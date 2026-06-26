{
    'name': 'Web App Switcher (Enterprise-like)',
    'version': '1.0.0',
    'category': 'Web',
    'summary': 'Add an Enterprise-like app switcher to Odoo Community',
    'depends': ['web', 'debranding'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'web_app_switcher/static/src/webclient/home_menu/home_menu.js',
            'web_app_switcher/static/src/webclient/home_menu/home_menu.xml',
            'web_app_switcher/static/src/webclient/home_menu/home_menu.scss',
            'web_app_switcher/static/src/webclient/navbar/navbar.js',
            'web_app_switcher/static/src/webclient/webclient.js',
            'web_app_switcher/static/src/webclient/web_app_switcher_templates.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
