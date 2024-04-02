# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug
from werkzeug.wrappers import Response

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class VisaNetController(http.Controller):
    _return_url = '/payment/visanet/return'

    @http.route(['/payment/visanet/return'], type='http', auth='public', csrf=False)
    def visanet_return(self, **data):
        """ Process the data returned by VisaNet after redirection.

        :param dict data: The feedback data
        """
        _logger.info('VisaNet: entering _handle_feedback_data with post data %s', pprint.pformat(data))  # debug
        request.env['payment.transaction'].sudo()._handle_feedback_data('visanet', data)
        #  request.redirect('/payment/status')

        response_return_url = data.pop('return_url', '/payment/status')
        
        headers = {
            'Location': response_return_url,
        }
                
        response = Response(response_return_url, status=302, headers=headers)
        if data.get('req_ship_to_address_city'):
            session_id = data.get('req_ship_to_address_city')
            # _logger.warn('req session_id: {}'.format(session_id))
            # _logger.warn('current session_id: {}'.format(request.session.sid))
            if session_id != request.session.sid:
                # _logger.warn('setting session_id: {}'.format(session_id))
                response.set_cookie('session_id', session_id, max_age=90 * 24 * 60 * 60, httponly=True)

        return response
