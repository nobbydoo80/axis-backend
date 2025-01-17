angular.module('axis')
.controller('EquipmentControlCenterBaseListController', function($scope, $http, $timeout, $window){
    $scope.userProcessingFormData = {
        equipment_ids: []
    };

    $scope.processingFormSubmit = function() {
        if ($scope.processingForm.$valid) {
            $http.post(
                '/api/v2/equipment_sponsor_status/change_state/',
                $scope.userProcessingFormData).then(function (response) {
                $window.location.reload();
            }, function (err) {
                alert(err.data);
            });
        }
    }

    $timeout(function () {
        var datatable = angular.element( document.querySelector('#DataTables_Table_0')).DataTable();
        datatable.on('select', function (e, dt, type, indexes) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.equipment_ids = dt.rows({selected: true}).ids().toArray();
            });
        }).on( 'deselect', function ( e, dt, type, indexes ) {
            $scope.$apply(function() {
                $scope.userProcessingFormData.equipment_ids = dt.rows({selected: true}).ids().toArray();
                if (!$scope.userProcessingFormData.equipment_ids.length) {
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
