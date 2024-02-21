# payment_visanet

Funciona con versión 15.0 de Odoo

Es necesario activar lo siguiente:
https://ebc2test.cybersource.com/ebc2/app/PaymentConfiguration/SecureAcceptanceSettings
* CVN en los tipos de tarjetas en Payment Settings
* Fails en AVS y CVN en Payment Settings
* Single Page Form en Payment Form
* Billing information en Payment Form > Checkout Steps: https://www.sitio.com/payment/visanet/return
* Transaction Response Page en Customer Response:  ../payment/visanet/return
* Custom Cancel Response Page en Customer Response: ../payment/visanet/return
