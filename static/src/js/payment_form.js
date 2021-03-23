odoo.define('payment_visanet.payment_form', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var PaymentForm = require('payment.payment_form');

    var _t = core._t;

    PaymentForm.include({

        willStart: function () {
            var recaptcha_v3_site_key = $('[name="recaptcha_v3_site_key"]').val();
            return this._super.apply(this, arguments).then(function () {
                return ajax.loadJS("https://www.google.com/recaptcha/api.js?render="+recaptcha_v3_site_key);
            })
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        payEvent: function (ev) {
            var recaptcha_v3_site_key = $('[name="recaptcha_v3_site_key"]').val();
            var self = this;
            var sup = this._super;
            var args = arguments;
            
            ev.preventDefault();
            grecaptcha.ready(function() {
                grecaptcha.execute(recaptcha_v3_site_key, {action: 'submit'}).then(function(token) {
                    return sup.apply(self, args);
                });
            });
        },
    });
});
