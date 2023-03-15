# coding: utf-8
import logging
import hmac
import hashlib
import base64
import uuid

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_visanet.controllers.payment import VisaNetController
from odoo.tools.float_utils import float_compare
from odoo.http import request

_logger = logging.getLogger(__name__)

signed_field_names = ['access_key', 'profile_id', 'transaction_uuid', 'signed_field_names', 'unsigned_field_names', 'signed_date_time', 'locale', 'transaction_type', 'reference_number', 'amount', 'currency', 'ship_to_address_city']

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'visanet':
            return res
        
        return_url = urls.url_join(self.acquirer_id.get_base_url(), VisaNetController._return_url),
        session_id = request.session.sid
        reference = self.reference
        transaction_date = fields.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        transaction_uuid = uuid.uuid4().hex
        unsigned_field_names = 'bill_to_forename,bill_to_surname,bill_to_email,bill_to_address_line1,bill_to_address_line2,bill_to_address_postal_code,bill_to_address_city,bill_to_address_state,bill_to_address_country,bill_to_phone'
        language = 'es-es'
        transaction_type = 'sale'
        currency = self.currency_id.name
        visanet_partner_address1 = self.partner_id.street[0:35] if self.partner_id.street else ''
        visanet_partner_address2 = self.partner_id.street2[0:35] if self.partner_id.street2 else ''

        signed_field_values = [self.acquirer_id.visanet_access_key, self.acquirer_id.visanet_profile_id, transaction_uuid, ','.join(signed_field_names), unsigned_field_names, transaction_date, language, transaction_type, reference, self.amount, currency, session_id]

        signed_string = []
        for i in range(len(signed_field_names)):
            signed_string.append(signed_field_names[i]+"="+str(signed_field_values[i]))

        key = bytes(self.acquirer_id.visanet_secret_key, 'utf-8')
        message = bytes(','.join(signed_string), 'utf-8')

        rendering_values = {
            'api_url': self.acquirer_id._visanet_get_api_url(),
            'visanet_access_key': self.acquirer_id.visanet_access_key,
            'visanet_secret_key': self.acquirer_id.visanet_secret_key,
            'visanet_profile_id': self.acquirer_id.visanet_profile_id,
            'visanet_amount': self.amount,
            'visanet_reference': reference,
            'visanet_uuid': transaction_uuid,
            'visanet_session_id': session_id,
            'visanet_date': transaction_date,
            'visanet_language': language,
            'visanet_transaction_type': transaction_type,
            'visanet_currency': currency,
            'visanet_partner_forename': self.partner_id.name,
            'visanet_partner_surname': '',
            'visanet_partner_email': self.partner_id.email,
            'visanet_partner_postal_code': self.partner_id.zip,
            'visanet_partner_city': self.partner_id.city,
            'visanet_partner_state': self.partner_id.state_id.code,
            'visanet_partner_country': self.partner_id.country_id.code,
            'visanet_partner_phone': self.partner_id.phone,
            'visanet_partner_address1': visanet_partner_address1,
            'visanet_partner_address2': visanet_partner_address2,
            'visanet_signed_field_names': ','.join(signed_field_names),
            'visanet_unsigned_field_names': unsigned_field_names,
            'visanet_signature': base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode("utf-8"),
        }
        return rendering_values

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'visanet':
            return tx
        
        reference = data.get('req_reference_number')
        if not reference:
            error_msg = _('VisaNet: received data with missing reference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference), ('provider', '=', 'visanet')])
        _logger.info(tx)

        if not tx or len(tx) > 1:
            error_msg = _('VisaNet: received data for reference %s') % (reference)
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple orders found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'visanet':
            return
        
        self.acquirer_reference = data.get('req_reference_number')
        status_code = data.get('decision', 'ERROR')
        if status_code == 'ACCEPT':
            self._set_done()
        else:
            error = 'VisaNet: error '+data.get('message')
            _logger.info(error)
            self._set_error(_("Your payment was refused (code %s). Please try again.", status_code))
