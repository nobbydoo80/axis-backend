angular.module('examineApp')

.controller('SubdivisionFormController', function($scope, $http, Actions){
    var endpointTemplates = {
        subdivision: '/api/v2/subdivision/[[id]]/',
        community: '/api/v2/community/[[id]]/'
    };
    var toPopulate = ['city', 'cross_roads', 'is_multi_family'];

    function updateFetchedFields(community){
        var subdivision = $scope.regionObject.object;
        if (!subdivision.city) {
            var element = $scope.region.axisFields.city;
            var elementScope = angular.element(element.find('[ui-select-helper]')).scope();
            elementScope.selectOptions.push(
                {'id': community.city, 'text': community.city_name}
            );
            subdivision.city = community.city;
        }
        if (!subdivision.cross_roads) {
            subdivision.cross_roads = community.cross_roads;
        }

        // Aggressively overwrite the multi-family setting to match
        subdivision.is_multi_family = community.is_multi_family;
    }
    function updateCommunity(subdivision){
        var element = $scope.region.axisFields.community;
        var elementScope = angular.element(element.find('[ui-select-helper]')).scope();
        elementScope.selectOptions.push({
            id: subdivision.community,
            text: subdivision.community_name
        });
        $scope.regionObject.object.community = subdivision.community;
        $scope.regionObject.object.community_name = subdivision.community_name;
    }

    // function hasEmptyFields(){
    //     var subdivision = $scope.regionObject.object;
    //     var hasEmpty = false;
    //     for (var i in toPopulate) {
    //         var value = subdivision[toPopulate[i]];
    //         hasEmpty = hasEmpty || (value == null || value === "")
    //     }
    //     return hasEmpty;
    // }

    function _apiCall(url, context){
        var endpoint = Actions.utils.formatUrl(url, context);
        return $http.get(endpoint, {}).error(function(data, code){
            console.log(data, code);
        });
    }

    var fn = {
        lookupCommunityInfo: function(){
            var community_id = $scope.regionObject.object.community,
                url = endpointTemplates.community,
                context = {id: community_id};
            if (community_id != null) {
                _apiCall(url, context).success(updateFetchedFields);
            }
        },

        validateMultiFamilySetting: function(){
            // Limit community choices based on this multi-family setting
            // $scope.fuckWith();
        },

        makeGeocodeDirty: function(){
            $scope.regionObject.object.address_override = false;
            $scope.regionObject.object.confirmed_address = false;
            $scope.regionObject.object.geocode_response = null;
        },

        // Not in use
        lookupSubdivisionCommunity: function(){
            var subdivision_id = $scope.regionObject.object.name,
                is_multi_family = $scope.regionObject.object.is_multi_family,
                url = endpointTemplates.subdivision,
                context = {id: subdivision_id};
            _apiCall(url, context).success(updateCommunity);
        }
    };

    angular.extend($scope, fn);
})

.run(function($rootScope, $http, Actions, RegionService){

    function reloadHistory(regionObject){
        $('[id^=history][id$=wrapper].dataTables_wrapper table').each(function(i, el){
            $(el).dataTable().fnDraw();
        });

        return regionObject;
    }

    function clearQAFields(regionObject){
        // The way we merge the objects that return from the server don't always clear values.
        regionObject.object.new_state = null;
        regionObject.object.result = null;
        regionObject.object.note = null;
        regionObject.object.observation_types = [];
        return regionObject;
    }

    function noopActionHandler(regionObject){
        return regionObject;
    }

    Actions.addPostMethodToType('save', ['subdivision', 'subdivision_documents', 'base_floorplan'], reloadHistory);
    Actions.addPostMethodToType('save', 'qa_status', clearQAFields);
    Actions.addMethod('manage_observations', noopActionHandler);
    Actions.addMethod('financial_checklist', function(regionObject){
        return $http.post(regionObject.helpers.standarddisclosuresettings.url, regionObject.object);
    });
    Actions.addMethod('permitandoccupancysettings', function(regionObject){
        return $http.post(regionObject.helpers.permitandoccupancysettings.url, regionObject.object)
            .then(function(){
                Actions.callMethod('reload', regionObject);
            });
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
});
