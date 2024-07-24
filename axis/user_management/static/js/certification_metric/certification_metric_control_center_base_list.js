angular.module('axis')
.controller('CertificationMetricControlCenterListController', function($scope, $http, $timeout, $window){
    $scope.userProcessingFormData = {
        certification_metric_ids: []
    };

    $timeout(function () {
        var datatable = angular.element( document.querySelector('#DataTables_Table_0')).DataTable();
        datatable.on('select', function (e, dt, type, indexes) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.certification_metric_ids = dt.rows({selected: true}).ids().toArray();
            });
        }).on( 'deselect', function ( e, dt, type, indexes ) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.certification_metric_ids = dt.rows({selected: true}).ids().toArray();
                if (!$scope.userProcessingFormData.certification_metric_ids.length) {
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
