angular.module('examineApp')

.controller('CommunityFormController', function($scope, $http, $interpolate){
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

.run(function($rootScope, Actions, RegionService){

    function reloadHistory(regionObject){
        $('[id^=history][id$=wrapper].dataTables_wrapper table').each(function(i, el){
            $(el).dataTable().fnDraw();
        });

        return regionObject;
    }

    Actions.addPostMethodToType('save', 'community', reloadHistory);
});
