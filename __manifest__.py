# -*- coding: utf-8 -*-

{
    'name': 'VisaNet Payment Acquirer',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Payment Acquirer: VisaNet Implementation',
    'version': '2.0',
    'description': """VisaNet Payment Acquirer""",
    'author': 'aquíH',
    'website': 'http://aquih.com/',
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_visanet_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'Other OSI approved licence',
}
