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

    @http.route(['/payment/visanet/return'], type='http', auth='public', csrf=False, save_session=False)
    def visanet_return(self, **data):
        """ Process the data returned by VisaNet after redirection.

        :param dict data: The feedback data
        """
        if data:
            _logger.info('VisaNet: entering _handle_feedback_data with post data %s', pprint.pformat(data))  # debug
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('visanet', data)
            tx_sudo._process_notification_data('visanet', data)

        return request.redirect('/payment/status')