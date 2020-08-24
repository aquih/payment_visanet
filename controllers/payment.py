# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request
from odoo.release import version_info

_logger = logging.getLogger(__name__)

class VisaNetController(http.Controller):
    _return_url = '/payment/visanet/return'

    @http.route([
        '/payment/visanet/return',
    ], type='http', auth='none', csrf=False)
    def visanet_return(self, **post):
        """ VisaNet """
        _logger.info('VisaNet: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'visanet')
        _logger.warn(post)
        if version_info[0] > 11:
            return werkzeug.utils.redirect(post.pop('return_url', '/payment/process'))
        else:
            return werkzeug.utils.redirect(post.pop('return_url', '/'))
