angular.module('examineApp')

.controller('CompanyFormController', function($scope, $http, $interpolate){
    var fn = {
        /* To be called via on-change by fields that make the existing geocoded result dirty. */
        makeGeocodeDirty: function(){
            $scope.regionObject.object.address_override = false;
            $scope.regionObject.object.confirmed_address = false;
            $scope.regionObject.object.geocode_response = null;
        },
    };

    angular.extend($scope, fn);
})

.controller('SamplingProviderApprovalController', function($scope){
    function _setApproval(url, button){
        var button = $(button);
        var buttons = button.closest('form').find('button');
        buttons.attr('disabled', 'disabled')
        $.post(url)
            .done(function(data){
                console.log(data);
                $scope.regionObject.helpers.current_sampling_approval_setting = data['has_approval'];
                $scope.$digest();
            })
            .always(function(){
                buttons.removeAttr('disabled');
            });
        return false;
    }

    function approve(button){
        return _setApproval($scope.regionObject.helpers.approval_url, button);
    }
    function unapprove(button){
        return _setApproval($scope.regionObject.helpers.unapproval_url, button);
    }

    return {
        'approve': approve,
        'unapprove': unapprove
    }
})

.controller('CompanyEquipmentController', function ($scope, $http, Actions) {
    $scope.stacked = [];

    $scope.stateMap = {
        'new': 'info',
        'active': 'success',
        'expired': 'warning',
        'rejected': 'danger'
    };

    $scope.companySponsorStatusGrouppedByState = {
        'new': [],
        'active': [],
        'expired': [],
        'rejected': []
    };

    $scope.stackedProgessBar = [];

    $scope.calculateProgressBar = function() {
        $scope.regionObject['object']['company_sponsor_status'].forEach(function (company_sponsor_status) {
            if (angular.isUndefined($scope.companySponsorStatusGrouppedByState[company_sponsor_status.state])) {
                $scope.companySponsorStatusGrouppedByState[company_sponsor_status.state] = [];
            }
            $scope.companySponsorStatusGrouppedByState[company_sponsor_status.state].push(company_sponsor_status);
        });

        for (var state in $scope.companySponsorStatusGrouppedByState) {
            if ($scope.regionObject['object']['company_sponsor_status'].length) {
                if ($scope.companySponsorStatusGrouppedByState.hasOwnProperty(state)) {
                    $scope.stackedProgessBar.push({
                        value: $scope.companySponsorStatusGrouppedByState[state].length*100/$scope.regionObject['object']['company_sponsor_status'].length || 0,
                        type: $scope.stateMap[state]
                    })
                }
            }
        }
    }

    $scope.createNewEquipment = function () {
        $scope.region.addProcessingStatus('create-new-equipment');
        $http.post('/api/v2/company/equipment/'+$scope.regionObject['object']['id']+'/copy_expired_equipment/', {}).then(function (response) {
            $scope.regionSet.fetchNewRegion({'activeState': 'default'}).then(function (newRegion) {
                var newObject = response.data;
                $scope.region.clearProcessingStatus('create-new-equipment');
                newRegion['object'] = angular.copy(newObject);
                newRegion['actions'] = angular.copy($scope.regionObject['actions']);
                $scope.regionSet.removeRegion($scope.regionObject);
            });
        }).catch(function (err) {
            console.log(err);
        });
    }

    $scope.calculateProgressBar();
    Actions.addPostMethodToType('save', 'company_equipment', function () {
        $scope.calculateProgressBar();
    })
})

.run(function($rootScope, $http, Actions){
    var object_id = window.__primary_object_id;

    Actions.addPreMethodToType('save', 'company_documents', function(regionObject){
        regionObject.object.object_id = object_id;
    });

    Actions.addMethod('financial_checklist', function(regionObject){
        return $http.post(regionObject.helpers.standarddisclosuresettings.url, regionObject.object);
    });
    Actions.addMethod('clear_financial_checklist', function(regionObject){
        var data = regionObject.helpers.standarddisclosuresettings.question_data;
        for (var i in data) {
            for (var j in data[i].items) {
                var name = data[i].items[j].name;
                regionObject.object[name] = data[i].items[j].null_value;
            }
        }
        return regionObject;
    });

    Actions.addMethod('permitandoccupancysettings', function(regionObject){
        return $http.post(regionObject.helpers.permitandoccupancysettings.url, regionObject.object)
            .then(function(){
                Actions.callMethod('reload', regionObject);
            });
    });
    Actions.addMethod('clear_permitandoccupancysettings', function(regionObject){
        var data = regionObject.helpers.permitandoccupancysettings.question_data;
        for (var i in data) {
            for (var j in data[i].items) {
                var name = data[i].items[j].name;
                regionObject.object[name] = data[i].items[j].null_value;
            }
        }
        return regionObject;
    });

    $rootScope.$on("addedRegion:company_documents", function(e, regionObject){
        regionObject.region_dependencies = {};
    });
}).controller('CompanyShippingAddressController', function($scope, $rootScope, $http, $timeout, $window, Actions) {

    $scope.differentShippingAddress = function () {
        return Boolean(
            $scope.regionObject.object.shipping_geocode_street_line1 ||
            $scope.regionObject.object.shipping_geocode_street_line2 ||
            $scope.regionObject.object.shipping_geocode_city ||
            $scope.regionObject.object.shipping_geocode_zipcode
        );
    }();

    $scope.mailingCity = $scope.regionObject.object['city_name'];

    $scope.regionObject.object['shipping_geocode_city'] = {
        text: $scope.regionObject.object['shipping_geocode_city_display'],
        value: $scope.regionObject.object['shipping_geocode_city']
    };

    $scope.useDifferentShippingAddress = function () {
        $scope.differentShippingAddress = !$scope.differentShippingAddress;

        $scope.regionObject.object.shipping_geocode_street_line1 = '';
        $scope.regionObject.object.shipping_geocode_street_line2 = '';
        $scope.regionObject.object.shipping_geocode_city = '';
        $scope.regionObject.object.shipping_geocode_zipcode = '';
    }

    $scope.mailingCityChanged = function ($item) {
        $scope.mailingCity = $item.text;
    }

    Actions.addPreMethodToType('save', ['user'], function (regionObject) {
        if (regionObject.object['shipping_geocode_city'] && regionObject.object['shipping_geocode_city']['value']) {
            regionObject.object['shipping_geocode_city'] = regionObject.object['shipping_geocode_city']['value'];
        }
        return regionObject;
    });
});
