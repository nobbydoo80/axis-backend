angular.module('axis')
.controller('CoreProfileController', function($scope, $rootScope, $http, $timeout, $window, Actions){

}).controller('UserFormProfileController', function($scope, $rootScope, $http, $timeout, $window, Actions){

    $scope.differentShippingAddress = function () {
        return Boolean(
            $scope.regionObject.object.shipping_geocode_street_line1 ||
            $scope.regionObject.object.shipping_geocode_street_line2 ||
            $scope.regionObject.object.shipping_geocode_city ||
            $scope.regionObject.object.shipping_geocode_zipcode
        );
    }();

    $scope.mailingCity = $scope.regionObject.object['mailing_geocode_city_display'];
    $scope.regionObject.object['mailing_geocode_city'] = {text: $scope.regionObject.object['mailing_geocode_city_display'], value: $scope.regionObject.object['mailing_geocode_city']};
    $scope.regionObject.object['shipping_geocode_city'] = {text: $scope.regionObject.object['shipping_geocode_city_display'], value: $scope.regionObject.object['shipping_geocode_city']};

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
        if (regionObject.object['mailing_geocode_city'] && regionObject.object['mailing_geocode_city']['value']) {
            regionObject.object['mailing_geocode_city'] = regionObject.object['mailing_geocode_city']['value'];
        }

        if (regionObject.object['shipping_geocode_city'] && regionObject.object['shipping_geocode_city']['value']) {
            regionObject.object['shipping_geocode_city'] = regionObject.object['shipping_geocode_city']['value'];
        }
        return regionObject;
    });

    $scope.signature = {
        enabled: false,
        fileName: '',
        sourceImage: null,
        resultImage: null,
        cropper: {
            actions: {
                rotateLeft: {
                    label: '<i class="fa fa-fw fa-rotate-left"></i>',
                    attrs: {'class': "btn btn-default btn-xs"}
                },
                rotateRight: {
                    label: '<i class="fa fa-fw fa-rotate-right"></i>',
                    attrs: {'class': "btn btn-default btn-xs"}
                },
                zoomIn: {
                    label: '<i class="fa fa-fw fa-search-plus"></i>',
                    attrs: {'class': "btn btn-default btn-xs"}
                },
                zoomOut: {
                    label: '<i class="fa fa-fw fa-search-minus"></i>',
                    attrs: {'class': "btn btn-default btn-xs"}
                },
                fit: {
                    label: '<i class="fa fa-fw fa-arrows-alt"></i>',
                    attrs: {'class': "btn btn-default btn-xs"}
                },
                crop: {
                    label: '<i class="fa fa-fw fa-crop"></i> Use this view',
                    attrs: {'class': "btn btn-primary btn-xs"}
                },
                select: {
                    label: '<label for="signature_upload"><i class="fa fa-fw fa-file-o"></i> Pick new image&hellip;</label>',
                    attrs: {'class': "btn btn-default btn-xs"}
                },

            },
            cropCallback: function (base64) {
                $scope.signature.resultImage = base64;

                $scope.regionObject.object.signature_image = null;
                $scope.regionObject.object.signature_image_raw = base64;
                $scope.regionObject.object.signature_image_raw_name = angular.copy($scope.signature.fileName);
                $scope.$apply();
            }
        },
        remove: function(){
            $scope.signature.sourceImage = null;
            $scope.signature.resultImage = null;
            $scope.signature.fileName = null;

            $scope.regionObject.object.signature_image = null;
            $scope.regionObject.object.signature_image_raw = null;
            $scope.regionObject.object.signature_image_raw_name = null;
        }
    };

    if ($scope.regionObject.object.signature_image) {
        $http.get($scope.regionObject.object.signature_image, { responseType: 'blob' }).then(function onSuccess(response) {
            var blob = response.data;
            var fileURL = URL.createObjectURL(blob);
            var index = $scope.regionObject.object.signature_image.lastIndexOf("/") + 1;
            $scope.signature.enabled = true;
            $scope.signature.sourceImage = fileURL;
            $scope.signature.resultImage = fileURL;
            $scope.signature.fileName = $scope.regionObject.object.signature_image.substr(index);
        });
    }

    $scope.signatureChanged = function () {
        var file = angular.element('#signature_upload')[0].files[0];
        var reader = new FileReader();
        reader.addEventListener("load", function () {
            // There's a bug in the image cropper than doesn't listen to ``image-url``
            // changes, so we have put "ng-if" on the element to make it unload entirely
            // when we set ``enabled`` to false.
            $scope.signature.enabled = false;
            $scope.$apply();
            // Now put the new image in the source field.
            $scope.signature.enabled = true;
            $scope.signature.sourceImage = reader.result;
            $scope.signature.fileName = file.name;
            $scope.$apply();
        }, false);
        if (file) {
            reader.readAsDataURL(file);
        }
    }
}).controller('UserTrainingController', function ($scope, $http, Actions) {
    $scope.stateMap = {
        'new': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'expired': 'warning'
    };

    $scope.trainingStatusGrouppedByState = {
        'new': [],
        'approved': [],
        'rejected': [],
        'expired': []
    };

    $scope.stackedProgessBar = [];

    $scope.calculateProgressBar = function() {
        $scope.regionObject['object']['training_statuses'].forEach(function (training_status) {
            if (angular.isUndefined($scope.trainingStatusGrouppedByState[training_status.state])) {
                $scope.trainingStatusGrouppedByState[training_status.state] = [];
            }
            $scope.trainingStatusGrouppedByState[training_status.state].push(training_status);
        });

        for (var state in $scope.trainingStatusGrouppedByState) {
            if ($scope.regionObject['object']['training_statuses'].length) {
                if ($scope.trainingStatusGrouppedByState.hasOwnProperty(state)) {
                    $scope.stackedProgessBar.push({
                        value: $scope.trainingStatusGrouppedByState[state].length*100/$scope.regionObject['object']['training_statuses'].length || 0,
                        type: $scope.stateMap[state]
                    })
                }
            }
        }
    }

    $scope.calculateProgressBar();
    Actions.addPostMethodToType('save', 'user_training', function () {
        $scope.calculateProgressBar();
    });
}).controller('UserAccreditationController', function ($scope, $http, Actions) {

}).controller('UserCertificationMetricController', function ($scope, $http, Actions) {

}).controller('UserInspectionGradingController', function ($scope, $http, Actions) {

});
