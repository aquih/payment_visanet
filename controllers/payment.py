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
    def visanet_return(self, **post):
        """ VisaNet """
        _logger.info('VisaNet: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'visanet')
        _logger.warn(post)
        
        response_return_url = post.pop('return_url', '/payment/process')
        
        headers = {
            'Location': response_return_url,
            #'X-Openerp-Session-Id': 'eb89202cb7b73e3653cc3952ea54336a993422d6',
        }
                
        response = Response(response_return_url, status=302, headers=headers)
        if post.get('req_ship_to_address_city'):
            session_id = post.get('req_ship_to_address_city')
            _logger.warn('req session_id: {}'.format(session_id))
            _logger.warn('current session_id: {}'.format(request.session.sid))
            if session_id != request.session.sid:
                _logger.warn('setting session_id: {}'.format(session_id))
                response.set_cookie('session_id', session_id, max_age=90 * 24 * 60 * 60, httponly=True)

        return response
