# -*- coding: utf-8 -*-

{
    'name': 'VisaNet Payment Provider',
    'category': 'Accounting/Payment Providers',
    'summary': 'Payment Provider: VisaNet Implementation',
    'version': '2.1',
    'description': """VisaNet Payment Provider""",
    'author': 'aquíH',
    'website': 'http://aquih.com/',
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_visanet_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'Other OSI approved licence',
}
