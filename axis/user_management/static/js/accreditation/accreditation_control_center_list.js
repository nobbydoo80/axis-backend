angular.module('axis')
.controller('AccreditationControlCenterListController', function($scope, $http, $timeout, $window, $location){
    $scope.userProcessingFormData = {
        accreditation_ids: []
    };

    $scope.busy = false;
    $scope.advancedFilters = true;

    $scope.processingFormSubmit = function() {
        if ($scope.processingForm.$valid) {
            $scope.busy = true;
            $http.patch(
                '/api/v2/accreditation/change_state/',
                $scope.userProcessingFormData
            ).then(function (response) {
                $scope.busy = false;
                $window.location.reload();
            });
        }
    }

    $scope.createReport = function() {
        $scope.busy = true;
        $http.get(
            '/api/v2/accreditation/create_approver_report/',
            {
                params: getUrlParameters()
            }
        ).then(function (response) {
            $scope.busy = false;
            if (response.data && response.data.asynchronous_process_document_url) {
                $window.open(response.data.asynchronous_process_document_url, '_blank');
            }
        });
    }

    $scope.createCustomerHIRLReport = function () {
        $scope.ngbs_verifier_report_busy = true;
        $http.get(
            '/api/v2/accreditation/create_customer_hirl_report/',
            {
                params: getUrlParameters()
            }
        ).then(function (response) {
            $scope.ngbs_verifier_report_busy = false;
            if (response.data && response.data.asynchronous_process_document_url) {
                $window.open(response.data.asynchronous_process_document_url, '_blank');
            }
        });
    }

    $timeout(function () {
        var datatable = angular.element( document.querySelector('#DataTables_Table_0')).DataTable();
        datatable.on('select', function (e, dt, type, indexes) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.accreditation_ids = dt.rows({selected: true}).ids().toArray();
            });
        }).on( 'deselect', function ( e, dt, type, indexes ) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.accreditation_ids = dt.rows({selected: true}).ids().toArray();
                if (!$scope.userProcessingFormData.accreditation_ids.length) {
                    $scope.userProcessingFormData = {};
                    if ($scope.processingForm) {
                        $scope.processingForm.$setPristine();
                        $scope.processingForm.$setUntouched();
                    }
                }
            });
        });
    }, 0);
});
