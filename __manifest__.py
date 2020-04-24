# -*- coding: utf-8 -*-

{
    'name': 'VisaNet Payment Acquirer',
    'category': 'Accounting/Payment',
    'summary': 'Payment Acquirer: VisaNet Implementation',
    'version': '1.0',
    'description': """VisaNet Payment Acquirer""",
    'author': 'José Rodrigo Fernández Menegazzo',
    'website': 'http://aquih.com/',
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_visanet_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
