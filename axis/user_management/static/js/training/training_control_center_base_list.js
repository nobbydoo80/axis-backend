angular.module('axis')
.controller('TrainingControlCenterBaseListController', function($scope, $http, $timeout, $window){
    $scope.userProcessingFormData = {
        training_ids: [],
        state_notes: ''
    };

    $scope.processingFormSubmit = function() {
        if ($scope.processingForm.$valid) {
            $http.post(
                '/api/v2/training_status/change_state/',
                $scope.userProcessingFormData
            ).then(function (response) {
                $window.location.reload();
            }, function (err) {
                alert(err.data);
            });
        }
    }

    $scope.createReport = function(training_status_state) {
        $scope.busy = true;
        $http.get(
            '/api/v2/training/create_approver_report/',
            {
                params: angular.extend(
                    {training_status_state: training_status_state},
                    getUrlParameters())
            }
        ).then(function (response) {
            $scope.busy = false;
            if (response.data && response.data.asynchronous_process_document_url) {
                $window.open(response.data.asynchronous_process_document_url, '_blank');
            }
        });
    }

    $timeout(function () {
        var datatable = angular.element( document.querySelector('#DataTables_Table_0')).DataTable();
        datatable.on('select', function (e, dt, type, indexes) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.training_ids = dt.rows({selected: true}).ids().toArray();
            });
        }).on( 'deselect', function ( e, dt, type, indexes ) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.training_ids = dt.rows({selected: true}).ids().toArray();
                if (!$scope.userProcessingFormData.training_ids.length) {
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
