angular.module('examineApp').run(function($q, Actions, $timeout, $http){
    var placeFields = ['lot_number', 'street_line1', 'street_line2', 'zipcode', 'county', 'cross_roads', 'state'];
    var cancelButton = $("<button type='button' class='btn btn-default'> No, I'll change it.</buttono>");
    var continueButton = $("<button type='button' class='btn btn-primary'>Continue</button>");
    var ajax_response_strings = {
        aborted: {
            title: "Geocoding cancelled",
            content: "<p>This appears to be taking longer than expected. Continue without Geocoding?</p>"
        },
        no_matches: {
            title: "Location not found",
            content: "<p>We could not find a location for the information you gave us. Is that okay?</p>",
            continue: 'Yes, continue'
        },
        multiple_matches: {
            title: "Select a location",
            content: {
                p: "<p>We found several locations matching the information you gave us. Please choose the one that is the most correct.</p>",
                ul: "<ul class='list-group'></ul>",
                more: "<p>If these are not correct, you may continue and we will use exactly the information you have provided.</p>"
            },
            continue: 'Continue as-is'
        },
        error: {
            title: "Error",
            content: "<p>We Encountered an Error. Continue without Geocoding?</p>"
        }
    };

    // HELPERS
    function _goButtonClickHandler(regionObject, deferred, submitButton){
        return function(e){
            if(e) e.preventDefault();
            _forwardToRealSave(deferred, regionObject);
            submitButton.popover('destroy');
        }
    }
    function _stopButtonClickHandler(regionObject, deferred, submitButton){
        return function(e){
            if(e) e.preventDefault();
            deferred.reject('Geocoding Cancelled');
            submitButton.popover('destroy');
        }
    }

    function _forwardToRealSave(deferred, regionObject) {
        // regionObject.commit_instruction = regionObject.helpers.original_commit_instruction;
        Actions.callMethod('save', regionObject).then(function(rObject){
            angular.extend(regionObject, rObject);
            deferred.resolve(regionObject);
        }, deferred.reject);
    }

    // REPONSE HANDLERS
    function noMatches(deferred, regionObject, submitButton){
        var strings = ajax_response_strings.no_matches,
            p = $(strings.content),
            goButton = continueButton.clone(),
            stopButton = cancelButton.clone();

        stopButton.on('click', _stopButtonClickHandler(regionObject, deferred, submitButton));
        goButton.on('click', _goButtonClickHandler(regionObject, deferred, submitButton));

        // change continue button text to match production
        goButton.text(strings.continue);

        submitButton.popover({
            title: strings.title,
            content: p.add(goButton).add(stopButton),
            placement: 'top',
            html: true
        });
        submitButton.popover('show');
        goButton.focus();
    }
    function oneMatch(deferred, regionObject, submitButton, matches){
        // This should be forwarding to save.
        var match = matches[0];
        regionObject.object.geocode_response = match.response;
        _forwardToRealSave(deferred, regionObject);
    }
    function multipleMatches(deferred, regionObject, submitButton, matches){
        var strings = ajax_response_strings.multiple_matches,
            goButton = continueButton.clone(),
            stopButton = cancelButton.clone(),
            p = $(strings.content.p),
            ul = $(strings.content.ul),
            more = $(strings.content.more),
            goButtonHandler = _goButtonClickHandler(regionObject, deferred, submitButton);

        stopButton.on('click', _stopButtonClickHandler(regionObject, deferred, submitButton));
        goButton.on('click', goButtonHandler);

        angular.forEach(matches, function(obj){
            var button = $("<a class='list-group-item' href='#'>" + obj.address + "</a>");
            button.on('click', function(e){
                e.preventDefault();
                regionObject.object.geocode_response = obj.response;
                $(this).closest('.list-group').find('.list-group-item').removeClass('active');
                $(this).addClass('active');
                goButtonHandler();
            });
            ul.append(button);
        });


        // change continue button text to match production
        goButton.text(strings.continue);

        submitButton.popover({
            title: strings.title,
            content: p.add(ul).add(more).add(goButton).add(stopButton),
            placement: 'top',
            html: true
        });
        submitButton.popover('show');

        // focus on the first option
        ul.find('a').first().focus();
    }
    function ajaxAbort(deferred, regionObject, submitButton){
        var strings = ajax_response_strings.aborted,
            goButton = continueButton.clone(),
            stopButton = cancelButton.clone(),
            p = $(strings.content);

        goButton.text('Yes, continue');

        stopButton.on('click', _stopButtonClickHandler(regionObject, deferred, submitButton));
        goButton.on('click', _goButtonClickHandler(regionObject, deferred, submitButton));

        submitButton.popover({
            title: strings.title,
            content: p.add(stopButton).add(goButton),
            html: true,
            placement: 'top'
        })
    }
    function ajaxError(deferred, regionObject, submitButton, error){
        var strings = ajax_response_strings.error,
            goButton = continueButton.clone(),
            stopButton = cancelButton.clone(),
            p = $(strings.content);

        if(error = 'INTERNAL SERVER ERROR'){
            _goButtonClickHandler(regionObject, deferred, submitButton)(null);
        } else {
            goButton.text('Yes, continue');
            var error = $("<p><b>Error: </b> <code>"+error+"</code></p>");

            stopButton.on('click', _stopButtonClickHandler(regionObject, deferred, submitButton));
            goButton.on('click', _goButtonClickHandler(regionObject, deferred, submitButton));

            submitButton.popover({
                title: strings.title,
                content: p.add(error).add(stopButton).add(goButton),
                placement: 'top',
                html: true
            });
            submitButton.popover('show');
        }

    }

    function examine_geocode(regionObject){
        var deferred = $q.defer();

        regionObject.$element.addClass('geo_form');

        var hasGeocodeFields = _.some(placeFields, function(key){
            return !!regionObject.object[key];
        });

        if (regionObject.object.confirmed_address || regionObject.object.address_override || !hasGeocodeFields){
            // Early return if geocoding looks like it should be bypassed
            _forwardToRealSave(deferred, regionObject);
        } else {
            // Perform geocode
            var element = regionObject.$element.find('.btn-primary');
            if(!element.length){
                element = $(".geocode-submit").first();
            }
            var data = _.clone(regionObject.object);
            delete data.raw_address;
            $http({
                method: 'GET',
                url: '/api/v2/geocode/matches/',
                params: data
            }).success(function(data){
                // debugger;
                var fns = [noMatches, oneMatch];
                // uses position to call depending on length. defaults to multiple.
                (fns[data.matches.length] || multipleMatches)(deferred, regionObject, element, data.matches);
            }).error(function(xhr, status, error){
                // debugger;
                if(status == 'abort' || status == 'timeout'){
                    ajaxAbort(deferred, regionObject, element);
                } else if(status == 'error'){
                    ajaxError(deferred, regionObject, element, error);
                } else {
                    ajaxError(deferred, regionObject, element, error);
                }
            });
        }

        return deferred.promise;
    }

    function preGeocodeValidate(regionObject){
        var errors = {};
        _.forIn(regionObject.fields, function(field, key){
            if(field.options.required){
                if(!regionObject.object[field.field_name]){
                    errors[field.field_name] = ['This field is required.'];
                }
            }
        });
        if(_.keys(errors).length){
            regionObject.controller.error(errors);
            return $q.reject('Form not valid.');
        }
        return $q.when(regionObject);
    }

    Actions.addMethod('geocode', examine_geocode);
    Actions.addPreMethod('geocode', preGeocodeValidate);
});
