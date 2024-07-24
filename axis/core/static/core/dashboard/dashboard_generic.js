angular.module('axis.dashboard.generic', ['axis.dashboard'])

.controller('MetricsController', function($scope, $http, $rootScope, $timeout){
    var ctrl = this;

    var controlTypes = [
        {prefix: '',                          endpoint: '/api/v2/qa/status/metrics/',                        params: {}},
        {prefix: 'program_',                  endpoint: '/api/v2/qa/status/program_metrics/',                params: {}},
        {prefix: 'file_',                     endpoint: '/api/v2/qa/status/rater_file_metrics/',             params: {}},
        {prefix: 'field_',                    endpoint: '/api/v2/qa/status/rater_field_metrics/',            params: {}},
        {prefix: 'eto_file_',                 endpoint: '/api/v2/qa/status/eto_rater_file_metrics/',         params: {}},
        {prefix: 'eto_field_',                endpoint: '/api/v2/qa/status/eto_rater_field_metrics/',        params: {}},
        {prefix: 'neearater_file_',           endpoint: '/api/v2/qa/status/neea_rater_file_metrics/',        params: {}},
        {prefix: 'neearater_field_',          endpoint: '/api/v2/qa/status/neea_rater_field_metrics/',       params: {}},
        {prefix: 'neeautility_file_',         endpoint: '/api/v2/qa/status/neea_rater_file_metrics/',        params: {}},
        {prefix: 'neeautility_field_',        endpoint: '/api/v2/qa/status/neea_rater_field_metrics/',       params: {}},
        {prefix: 'neeautility_cert_payment_', endpoint: '/api/v2/qa/status/neea_utility_certified_metrics/', params: {}},
        {prefix: 'neeautility_uncertified_',  endpoint: '/api/v2/eep_program/builder_program_metrics/',      params: {}},
        {prefix: 'builder_program_',          endpoint: '/api/v2/eep_program/builder_program_metrics/',      params: {filter_type: 'certification_date'}},
        {prefix: 'home_status_',              endpoint: '/api/v2/eep_program/builder_program_metrics/',      params: {filter_type: 'creation_date'}},
        {prefix: 'payment_status_',           endpoint: '/api/v2/eep_program/builder_program_metrics/',      params: {filter_type: 'certification_date'}}
    ]

    var controlNames = [
        'date_start',
        'date_end',
        'us_state',
        'utility',

        // Hidden
        'style'
    ];

    var widgetInit = {
        'date_start': function(e){ return e.datepicker() },
        'date_end': function(e){ return e.datepicker() },
        'us_state': function(e){ return e.select2() },
        'utility': function(e){ return e.select2() }
    }
    var widgetUpdaters = {
        // Do extra work to get a widget in sync with data
        'date_start': function(el, data){ el.datepicker('update', data) },
        'date_end': function(el, data){ el.datepicker('update', data) }
    }

    ctrl.loading = {};

    /* These attributes will be generated one for each prefix in the controlTypes above.
        (i.e., 'controls' and 'program_controls' and 'eto_file_controls' will all exist upon first
        api ajax json response for that prefix.)
    - controls
    - utility_choices
    - metrics_data (array of objects)
    - sums (object of keys to numbers)
    - loading (boolean)
    */

    function init(){

        // Every type of 'controls' prefix should show up here so that the values and widgets can be
        // initialized when the page loads.

        for (var i in controlTypes) {
            var typeInfo = controlTypes[i];
            var prefix = typeInfo.prefix;
            var endpoint = typeInfo.endpoint;
            var params = typeInfo.params;

            // Set up the default ng-model data for the allocated control
            ctrl[prefix + 'controls'] = {};
            _.forEach(controlNames, function(k){
                ctrl[prefix + 'controls'][k] = $('#'+prefix+'controls .field-'+k).val();
            });

            // Initialize loading status (update function will set to true on its own)
            ctrl.loading[prefix + 'loading'] = false;

            // Update function for control field onchange
            // var _update = _.debounce(updateFactory(prefix, endpoint, params), 500);
            var _update = _.debounce(updateFactory(prefix, endpoint, params), 500, {leading: true, trailing: true});
            ctrl[prefix + 'update'] = _update;

            // Initialize DOM widgets
            _.forEach(ctrl[prefix + 'controls'], function(v, k){
                ctrl[prefix + k] = _initControlField(prefix, k);
            });

            // Clear data store
            ctrl[prefix + 'metrics_data'] = null;

            // Do initial update
            _.forEach(ctrl[prefix + 'controls'], function(v, k){
                // ctrl[prefix + k].on('change', _update);
            });
            ctrl[prefix + 'update']();
        }

        function _initControlField(prefix, fieldName) {
            var element = $('#'+prefix+'controls .field-'+fieldName);
            var initFunction = widgetInit[fieldName];
            if (element.length && initFunction !== undefined) {
                element = initFunction(element);
            }
            return element;
        }

        function updateFactory(prefix, endpoint, params){
            return function update(){
                var url = endpoint + '?' + $.param(ctrl[prefix + 'controls']) + '&' + $.param(params);
                ctrl.loading[prefix + 'loading'] = true;
                $http.get(url).success(function(response){
                    // Save panel data
                    ctrl[prefix + 'controls'] = response.controls;
                    ctrl[prefix + 'utility_choices'] = response.choices.utility;
                    ctrl[prefix + 'metrics_data'] = Object.keys(response.data).length ? response.data : null;
                    ctrl[prefix + 'sums'] = response.sums;

                    // Make sure complex widgets are current if the server normalized the inputs
                    _.forEach(widgetUpdaters, function(v, k){
                        widgetUpdaters[k](ctrl[prefix + k], response.controls[k]);
                    });

                    // End the loading phase
                    ctrl.loading[prefix + 'loading'] = false;
                });
            }
        }
    }

    init();

    // URL helpers for links that want the controls serialized to GET params
    ctrl.getControlsAsParams = function(prefix){
        return $.param($('#'+prefix+'controls .form-control'));
    }

    // Builder Dashboard stuff (not a great place for it)
    ctrl.getTotalForKey = function(prefix, key){
        var data_name = prefix + "_metrics_data";
        return _.reduce(ctrl[data_name], function(sum, item){
            var value = key.split('.').reduce(function(obj, index){
                return obj[index];
            }, item) || 0;
            if (_.isString(value)){
                value = parseFloat(value.replace(/\,/g, ''));
            }
            return sum + value;
        }, 0)
    }
})
.directive('dashboardWidgetMetrics', function(){
    return {
        'restrict': 'A',
        'scope': true,
        'controller': 'MetricsController',
        'controllerAs': 'widget'
    }
})
