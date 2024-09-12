import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    util.records.rename_xmlid(cr, 'payment_visanet.payment_acquirer_visanet', 'payment_visanet.payment_provider_visanet')
    _logger.info("Campos borrados")