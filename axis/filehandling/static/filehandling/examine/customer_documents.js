angular.module('examineApp')
.controller('CustomerDocumentTabController', function($scope, $http, Actions, RegionService){
    $scope.downloadAllIsLoading = false;

    $scope.downloadAll = function (event, endpoint) {
        event.preventDefault();
        $scope.downloadAllIsLoading = true;

        $http.get(endpoint).then(function(response) {
            $scope.downloadAllIsLoading = false;
            window.open('/file-operation/document/' + response.data.id + '/', '_blank').focus();
        });
    };
})
.controller('MultipleDocumentController', function($scope, Actions, RegionService){
    var processing = false;

    $scope.region = {
        handleAction: function(action){
            processing = true;
            var regionObjects = RegionService.getRegionFromTypeName('home_documents'),
                regionObject = angular.isArray(regionObjects) ? regionObjects[0] : regionObjects;

            return Actions.callMethod(action, regionObject).finally(function(){
                processing = false;
            });
        },
        isProcessing: function(){
            return processing;
        },
        regionsEditing: _regionsEditing
    }
    function _regionsEditing(){
        return _.filter(RegionService.getRegionFromTypeName('home_documents'), function(region){
            return region.controller.editing();
        }).length;
    }

})
