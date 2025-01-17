/**
 * Created by mjeffrey on 11/20/14.
 */

angular.module('axis.services.Modal')
.factory('Modal', function($modal, $q, $http){
    function getExtraDataMethod(url){
        // create callable closure around the extra data url.
        return function(){
            var items = $q.defer();
            $http.get(url).success(function(data){
                return items.resolve(data);
            });
            return items.promise;
        }
    }

    return function Modal(action, regionObject){
        var resolves = {
            regionObject: function(){ return regionObject }
        };
        if (angular.isDefined(action.modal.dataUrl) && action.modal.dataUrl != null) {
            resolves['extraData'] = getExtraDataMethod(action.modal.dataUrl);
        } else {
            resolves['extraData'] = function(){ return null; };
        }

        var modal = $modal.open({
            templateUrl: action.modal.templateUrl,
            resolve: resolves,
            controller: 'ModalFactoryController',
            controllerAs: 'vm',
            size: action.modal.size
        });
        return modal.result;
    }

})
.controller('ModalFactoryController', function($scope, $modalInstance, regionObject, extraData){
    var vm = this;
    $scope.regionObject = vm.regionObject = regionObject;
    vm.extraData = extraData;
    vm.ok = function(){
        $modalInstance.close(vm.regionObject);
    };
    vm.cancel = function(){
        $modalInstance.dismiss('cancel');
    };
});
