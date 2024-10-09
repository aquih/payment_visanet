# -*- coding: utf-8 -*-

from . import models
from . import controllers

from odoo.addons.payment import setup_provider, reset_payment_provider

def post_init_hook(env):
    setup_provider(env, 'visanet')

def uninstall_hook(env):
    reset_payment_provider(env, 'visanet')