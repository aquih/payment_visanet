# coding: utf-8
import logging
import urllib
import random
import hmac
import hashlib
import base64
import uuid

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_visanet.controllers.payment import VisaNetController
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)

signed_field_names = ['access_key', 'profile_id', 'transaction_uuid', 'signed_field_names', 'unsigned_field_names', 'signed_date_time', 'locale', 'transaction_type', 'reference_number', 'amount', 'currency']

class AcquirerVisaNet(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('visanet', 'VisaNet')])
    visanet_access_key = fields.Char('Access Key', required_if_provider='visanet', groups='base.group_user')
    visanet_secret_key = fields.Char('Secret Key', required_if_provider='visanet', groups='base.group_user')
    visanet_profile_id = fields.Char('Profile ID', required_if_provider='visanet', groups='base.group_user')

    def visanet_form_generate_values(self, values):
        reference = values['reference']
        # reference = '1588094529374'
        transaction_date = fields.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        # transaction_date = '2020-04-28T17:57:28Z'
        transaction_uuid = uuid.uuid4().hex
        # unsigned_field_names = 'bill_to_forename,bill_to_surname,bill_to_email,bill_to_address_line1,bill_to_address_postal_code,bill_to_address_city,bill_to_address_state,bill_to_address_country,bill_to_phone,return_url'
        unsigned_field_names = 'bill_to_forename,bill_to_surname,bill_to_email,bill_to_address_line1,bill_to_address_postal_code,bill_to_address_city,bill_to_address_state,bill_to_address_country,bill_to_phone'
        language = 'es-es'
        transaction_type = 'sale'
        currency = 'GTQ'

        signed_field_values = [self.visanet_access_key, self.visanet_profile_id, transaction_uuid, ','.join(signed_field_names), unsigned_field_names, transaction_date, language, transaction_type, reference, values['amount'], currency]
        # signed_field_values = [self.visanet_access_key, self.visanet_profile_id, '5ea8669080690', ','.join(signed_field_names), unsigned_field_names, transaction_date, language, transaction_type, reference, values['amount'], currency]

        signed_string = []
        for i in range(len(signed_field_names)):
            signed_string.append(signed_field_names[i]+"="+str(signed_field_values[i]))

        key = bytes(self.visanet_secret_key, 'utf-8')
        message = bytes(','.join(signed_string), 'utf-8')

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        visanet_tx_values = dict(values)
        visanet_tx_values.update({
            'visanet_access_key': self.visanet_access_key,
            'visanet_secret_key': self.visanet_secret_key,
            'visanet_profile_id': self.visanet_profile_id,
            'visanet_amount': values['amount'],
            'visanet_reference': reference,
            'visanet_uuid': transaction_uuid,
            'visanet_date': transaction_date,
            'visanet_language': language,
            'visanet_transaction_type': transaction_type,
            'visanet_currency': currency,
            'visanet_signed_field_names': ','.join(signed_field_names),
            'visanet_unsigned_field_names': unsigned_field_names,
            'visanet_return': '%s' % urllib.parse.urljoin(base_url, VisaNetController._return_url),
            'visanet_signature': base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()),
        })
        return visanet_tx_values

    def visanet_get_form_action_url(self):
        if self.state == 'enabled':
            return "https://secureacceptance.cybersource.com/pay"
        else:
            return "https://testsecureacceptance.cybersource.com/pay"

class TxVisaNet(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _visanet_form_get_tx_from_data(self, data):
        """ Given a data dict coming from visanet, verify it and find the related
        transaction record. """
        origin_data = dict(data)
        reference = data.get('req_reference_number')
        if not reference:
            error_msg = _('VisaNet: received data with missing reference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('VisaNet: received data for reference %s') % (reference)
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _visanet_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        status_code = data.get('decision', 'ERROR')
                    
        if status_code == 'ACCEPT':
            if float_compare(float(data.get('auth_amount', '0.0')), self.amount, 2) != 0:
                invalid_parameters.append(('auth_amount', data.get('auth_amount'), '%.2f' % self.amount))

            signed_string = []
            for field in data.get('signed_field_names', '').split(','):
                signed_string.append(field+"="+data.get(field, ''))

            key = bytes(self.acquirer_id.visanet_secret_key, 'utf-8')
            message = bytes(','.join(signed_string), 'utf-8')
            sign = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode('utf-8')
            if data.get('signature', '') != sign:
                invalid_parameters.append(('signature', data.get('signature'), '%s' % sign))
                
        return invalid_parameters

    def _visanet_form_validate(self, data):
        status_code = data.get('decision', 'ERROR')
        vals = {
            "date": fields.datetime.now(),
            "acquirer_reference": data.get('transaction_id'),
        }
        if status_code == 'ACCEPT':
            self.write(vals)
            self._set_transaction_done()
            return True
        else:
            error = 'VisaNet: error '+data.get('message')
            _logger.info(error)
            self.write(vals)
            self._set_transaction_error(error)
            return False
