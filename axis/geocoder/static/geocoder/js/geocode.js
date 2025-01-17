/* geocode.js
 * This file contains plugins, functions, and whatever else is related to
 * geocoding geographic data in user-facing forms.
 *
 * Requires:
 *
 *     - jquery.validate.js
 */


/* geocodeForm plugin
 *
 * This plugin encapsulates the logic to setup validation and to geocode data
 * after data is validated.
 *
 * A targetted form should have a DOM attribute "data-geocoding-type" which is
 * set to one of 'subdivision', 'home', 'community', 'company'.
 *
 * Arguments:
 *
 *     options (Object):
 *         See $.fn.geocodeForm.defaults for defaults and documentation.
 *
 * Example:
 *
 *     // Current setup assumes that validate has already been called on the
 *     // form, e.g. $('#axis_form').validate(...);
 *     $('#axis_form').geocodeForm('subdivision');
 *
 */

// TODO: Handling of type feels odd. Make it smarter.
// TODO: Separate from above, the switch statements for type feel awkward,
// mostly because there are several of them. There as got to be a better way to
// encapsulate the differences for the different type of forms.

(function($) {
    var ESCAPE_KEY = 27;
    var AJAX_TIMEOUT = 3001;

    ajax_response_strings = {
        aborted: {
            title: "Geocoding cancelled",
            content: "<p>This appears to be taking longer than expected. Continue without Geocoding?</p>"
        },
        no_matches: {
            title: "Location not found",
            content: "<p>We could not find a location for the information you gave us. Is that okay?</p>"
        },
        multiple_matches: {
            title: "Select a location",
            content: {
                p: "<p>We found several locations matching the information you gave us. Please choose the one that is the most correct.</p>",
                ul: "<ul class='list-group'></ul>",
                more: "<p>If these are not correct, you may continue and we will use exactly the information you have provided.</p>"
            }
        },
        error: {
            title: "Error",
            content: "<p>We Encountered an Error. Continue without Geocoding?</p>"
        }
    };

    function ajax_response_setup(geoForm){
        var popover_options = $.extend(true, {}, geoForm.settings.popoverOptions, {'trigger': 'manual'});
        var $conButton = $('<button type="button" class="btn btn-primary continue"></button>'),
            // While a cancel button is not strictly needed here, as a user
            // can simply edit a geo field to reset the form, it is an affordance
            // that makes it obvious that they can edit and re-geocode.
            $canButton = $('<button type="button" class="btn btn-default">No, I’ll change it</button>');
        $canButton.on("click", geoForm.resetPopover);
        $conButton.on("click", function(event){
            $conButton.text("Submitting … ").prop("disabled", true);
            console.log("Submitting: " + geoForm.$geoFields.serialize())
            geoForm.submit();
        });
        return {
            'options': popover_options,
            'continue': $conButton,
            'cancel': $canButton
        }
    }
    function ajax_no_matches(geoForm, data){
        var cruft = ajax_response_setup(geoForm);
        var popover_options = cruft.options;
        var $canButton = cruft.cancel;
        var $conButton = cruft.continue;

        geoForm.$submitBtn.text("Continue?");

        var $p = $(ajax_response_strings.no_matches.content);
        $conButton.text("Yes, continue");

        popover_options.title = ajax_response_strings.no_matches.title;
        popover_options.content = $p.add($conButton).add($canButton);

        geoForm.$submitBtn.popover(popover_options);
        geoForm.$submitBtn.popover("show");
    }
    function ajax_one_match(geoForm, data){
        geoForm.$submitBtn.text("Submitting …");
        geoForm.submit(data.matches[0].response);
    }
    function ajax_multiple_matches(geoForm, data){
        var cruft = ajax_response_setup(geoForm);
        var popover_options = cruft.options;
        var $canButton = cruft.cancel;
        var $conButton = cruft.continue;

        geoForm.$submitBtn.text('Select one …');

        popover_options.title = ajax_response_strings.multiple_matches.title;

        var $p = $(ajax_response_strings.multiple_matches.content.p),
            $ul = $(ajax_response_strings.multiple_matches.content.ul),
            $more = $(ajax_response_strings.multiple_matches.content.more);
        $conButton.text("Continue as-is");
        popover_options.content = $p.add($ul).add($more).add($conButton).add($canButton);
        $.each(data.matches, function(index, value){
            $ul.append('<li class="list-group-item"><button type="button" class="btn btn-link" data-value="' + value.response + '">' + value.address + '</button></li>');
        });

        $ul.find('button').on('click', function(event){
            geoForm.resetPopover;
            $conButton.text("Submitting … ").prop("disabled", true);
            console.log("Submitting: " + geoForm.$geoFields.serialize())
            geoForm.submit($(event.target).data('value'));

        });
        geoForm.$submitBtn.popover(popover_options);
        geoForm.$submitBtn.popover('show');

    }
    function ajax_abort(geoForm, xhr){
        var cruft = ajax_response_setup(geoForm);
        var popover_options = cruft.options;
        var $canButton = cruft.cancel;
        var $conButton = cruft.continue;

        var $p = $(ajax_response_strings.aborted.content);
        $conButton.text("Yes, continue");

        popover_options.title = ajax_response_strings.aborted.title;
        popover_options.content = $p.add($conButton).add($canButton);

        geoForm.$submitBtn.popover(popover_options);
        geoForm.$submitBtn.popover("show");
    }
    function ajax_error(geoForm, xhr, error){
        var cruft = ajax_response_setup(geoForm);
        var popover_options = cruft.options;
        var $canButton = cruft.cancel;
        var $conButton = cruft.continue;

        if(error == "INTERNAL SERVER ERROR"){
            // TODO: need a place to put the error message
            $conButton.text("Submitting …").prop("disabled", true);
            geoForm.submit();
        } else {
            var $p = $(ajax_response_strings.error.content);

            $conButton.text("Yes, continue");
            var $error = $("<p><b>Error:</b> <code>" + error + "</code></p>");

            popoverOptions.title = ajax_response_strings.error.title;
            popoverOptions.content = $p.add($error).add($conButton).add($canButton);

            geoForm.$submitBtn.popover(popoverOptions);
            geoForm.$submitBtn.popover("show");
        }
    }

    // Main entry point to geocodeForm plugin.
    $.fn.geocodeForm = function (geocodingType, confirmedAddress, options) {
        var settings = $.extend(true, {}, $.fn.geocodeForm.defaults, options);
        // We use `this.each` just to be idiomatic, but in reality, we currently
        // only expect to be working on a single form element at a time.
        return this.each(function(index, form) {
            var $form = $(form);

            if (!$form.data('geoForm')) {
                if (!geocodingType) {
                    geocodingType = $form.data('geocoding-type');
                }
                if (!confirmedAddress) {
                    confirmedAddress = $form.data('confirmed-address');
                }
                if (typeof confirmedAddress == "string") {
                    confirmedAddress = confirmedAddress == "true";
                }
                new $.fn.geocodeForm.GeoForm(geocodingType, confirmedAddress, $form, settings);
            }
        });
    };

    $.fn.geocodeForm.GeoForm = function (type, confirmedAddress, $form, settings) {
        this.type = type;
        this.confirmedAddress = confirmedAddress;
        this.$form = $form;
        this.settings = settings;
        this.init();
    };

    $.extend($.fn.geocodeForm.GeoForm.prototype, {
        init: function () {
            this.$form.addClass('geo_form');
            this.next_geocode_attempt = null;
            if (window.location.pathname.indexOf("add") == -1) {
                // We want this to fire when on no adds.
                this.local_storage_string = "Geocode_" + window.location.pathname + "_next_geocode_time";
                this.next_geocode_attempt = localStorage.getItem(this.local_storage_string) || null;
            }
            this.has_changed = false;
            this.geocoded = false;
            this.request = null;
            // Enables us to get back to the GeoForm in validation submit handler.
            this.$form.data('geoForm', this);
            this.$submitBtn = this.$form.find('#id_submit');
            this.apiURL = '/api/v2/geocode/matches/';
            this.init_geo_fields();
            this.init_validation();

            $(document).on('keyup', function(e){
                if(e.keyCode == ESCAPE_KEY && this.request != null){
                    this.request.abort();
                }
            }.bind(this))
        },

        init_geo_fields: function () {
            var prefix = this.settings.prefix;
            this.$geocodeInput = this.$form.find('#id_' + (prefix ? prefix+"-" : "") + 'geocode_response');
            this.$geoFields = this.geoFields();

            $(this.$geoFields).on('change', function(){
                this.$geocodeInput.val("");
                this.has_changed = true;
            }.bind(this));

            // Include `keyup` so we reset if they change a field but do not
            // unfocus it. (Some geofields fit in the window with the submit
            // button at the same time.)
            this.$geoFields.on('change keyup', this.resetPopover);
        },

        geoFields: function () {
            var form_fields = {
                company: ['street_line1', 'street_line2', 'city', 'zipcode'],
                community: ['city', 'cross_roads'],
                home: ['lot_number', 'subdivision', 'street_line1', 'street_line2', 'city', 'zipcode', 'is_multi_family'],
                subdivision: ['community', 'city', 'cross_roads'],
                user: ['street_line1', 'street_line2', 'city', 'zipcode']
            };

            var prefix = this.settings.prefix;
            var geocoding_ids = $.map(form_fields[this.type], function(field_name, i){
                return "#id_" + (prefix ? prefix+"-" : "") + field_name;
            });

            return this.$form.find(geocoding_ids.join(','));
        },

        init_validation: function () {
            // .validate() returns a validator, which lets us at settings.
            // Here we set the GeoForm.geocode function as the handler used
            // once validation has proved the form ready-to-go.
            this.$form.validate().settings.submitHandler = this.geocode;

            // Now setup type-specific validation.
            switch (this.type) {
                case 'home':
                    // Do we need either/or handling for subdivision?
                    break;
                case 'subdivision':
                    this.$form.find("#id_city").rules('add', { required: true });
                    // Crossroads requirement was removed per request of github ticket #279
                    // this.$form.find("#id_cross_roads").rules('add', { required: true });
                    break;
            }
        },

        resetPopover: function (event) {
            var geoForm = $(this.form).data('geoForm');

            // Reset any geocoding prompts that are setup.
            if (geoForm.geocoded || geoForm.request) {
                geoForm.$submitBtn.popover('destroy');
                geoForm.$submitBtn.prop('disabled', false);
                geoForm.$submitBtn.text('Submit');
                geoForm.geocoded = false;
                // Abort any geocoding requests in progress because we are
                // going to need to send a new one anyway.
                if (geoForm.request) {
                    geoForm.request.abort();
                    geoForm.request = null;
                }
            }
        },

        // Once geocoding is complete, this function is used to submit the form.
        submit: function (pk) {
            if (pk!==undefined) {
                this.$geocodeInput.val(pk);
            }
            // Note that we call the native submit event, because calling
            // the jQuery one invokes validation, and thus recursion.
            var callback = this.settings.submitCallback;
            if (callback) {
                callback();
            } else {
                // Native submit.  Might blow up if there's a button on the page with the name
                // "submit", so try..catch tries to deal with it as directly as possible.
                try{
                    this.$form[0].submit();
                } catch(e){
                    $(this.$form[0].submit).replaceWith("<button type='button'>Submit</button>");
                    this.$form[0].submit();
                }
            }
        },

        clean_data: function(){
            // If the form has a prefix, we want to remove it so the geocoder just get confused
            var data = this.$geoFields.serialize();
            if(this.settings.prefix){
                data = data.replace(new RegExp("(^|&)"+this.settings.prefix+"-", "g"), "$1");
            }
            return data;
        },

        geocode: function (form, event) {
            // ``this`` is bound to the validator object that called this
            // function as a submit handler, so we have to get our GeoForm here.
            event.preventDefault();
            var geoForm = $(this.currentForm).data('geoForm');

            var current_time = +(new Date());
            // Explicit about Boolean type, just for clarity.
            var attempt_to_geocode = Boolean(current_time > geoForm.next_geocode_attempt);

            console.log("Confirmed: " + geoForm.confirmedAddress + " Attempt: " + attempt_to_geocode)

            if((!geoForm.confirmedAddress && attempt_to_geocode) || geoForm.has_changed){
                if (window.location.pathname.indexOf("add") == -1) {
                    geoForm.next_geocode_attempt = +(new Date()) + (24*60*60*1000);
                    localStorage.setItem(geoForm.local_storage_string, geoForm.next_geocode_attempt);
                }
                var data = geoForm.clean_data();

                // We store the request so we can cancel it later if necessary.
                geoForm.request = $.ajax({
                    url: geoForm.apiURL,
                    data: data,
                    timeout: AJAX_TIMEOUT,
                    beforeSend: function(jqXHR) {
                        geoForm.$submitBtn.prop('disabled', true);
                        // TODO: Soften the changing of button text with animation.
                        geoForm.$submitBtn.text('Geocoding …');
                    },
                    success: function(data) {
                        geoForm.geocoded = true;

                        $(this.currentForm).trigger("geocoded", [data]);

                        if(data.matches.length == 0){
                            ajax_no_matches(geoForm, data);
                        } else if(data.matches.length == 1){
                            ajax_one_match(geoForm, data);
                        } else {
                            ajax_multiple_matches(geoForm, data);
                        }
                    },
                    error: function(xhr, status, error){
                        if(status == 'abort' || status == 'timeout'){
                            ajax_abort(geoForm, xhr);
                        } else if(status == 'error'){
                            ajax_error(geoForm, xhr, error);
                        }
                    }
                });
            } else {
                geoForm.submit();
            }
        }
    });

    // Default settings for the geocodeForm plugin.
    $.fn.geocodeForm.defaults = {
        // TODO: Implement defaults where sensible, e.g. submit button selector,
        // api endpoint URL, popover options.

        'prefix': null,
        'submitCallback': null,
        'popoverOptions': {
            'placement': 'top',
            'html': true
        }
    }

}(jQuery));


jQuery.validator.addMethod('blank', function(value, element, param) {
    /* Custom validation method that requires that a field be empty. Its main
     * use case is when you have two mutually-exclusive fields, such that one
     * is required, but only one is allowed, such as with community and city on
     * a subdivision. This code is totally cribbed from the required method
     * that ships with jquery.validate.js.
     *
     * Example:
     *
     *     var messages = {
     *             required: 'Select either a Community or City',
     *             blank: 'Select only one of Community or City'
     *         };
     *     $("#id_community").rules('add', {
     *         required: {depends: '#id_city:blank'},
     *         blank: {depends: '#id_city:filled'},
     *         messages: messages
     *     });
     *     $("#id_city").rules('add', {
     *         required: {depends: '#id_community:blank'},
     *         blank: {depends: '#id_community:filled'},
     *         messages: messages
     *     });
     */

    // check if dependency is met
    if (!this.depend(param, element)) {
        return "dependency-mismatch";
    }

    if (element.nodeName.toLowerCase() === 'select') {
        // could be an array for select-multiple or a string, both are fine this way
        var val = jQuery(element).val();
        return !val;
    }

    if (this.checkable(element)) {
        return this.getLength(value, element) === 0;
    }

    return jQuery.trim(value).length === 0;
}, "This field must be blank.");
