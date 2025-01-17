/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.maps')
.controller('MapController', function($scope, ExtraMapMarkers){

    var vm = this;
    if(angular.isUndefined($scope.regionObject)){
        throw new Error("MapController must be placed in a scope with access to 'regionObject'.");
    }

    vm.map = {
        center: {
            latitude: $scope.regionObject.object.latitude,
            longitude: $scope.regionObject.object.longitude
        },
        zoom: 15,
        options: {
            scrollwheel: false,
            streetViewControl: false,
            zoomControlOptions: {style: 'SMALL'},
            mapTypeControlOptions: {style: 'DROPDOWN_MENU'}
        }
    };

    vm.showMap = getShowMap();
    vm.extraMarkers = ExtraMapMarkers;

    vm.mainMarker = {
        coords: {
            latitude: $scope.regionObject.object.latitude,
            longitude: $scope.regionObject.object.longitude
        },
        id: $scope.regionObject.object.id,
        show: false,
        info: {visible: true},
        windowOptions: {visible: false},
        rawAddress: getRawAddress(),
        geocodedAddress: getGeocodedAddress()
    };
    vm.extraMarkers.unshift(createMarker(vm.mainMarker));

    $scope.$watchGroup(['regionObject.object.latitude', 'regionObject.object.longitude'], _.debounce(setShowMap, 1000));

    function createMarker(marker){
        marker.onClick = function(){
            marker.show = !marker.show;
        };
        marker.link = getLink;
        marker.link = marker.link();
        return marker;
    }
    function getRawAddress(){
        if($scope.regionObject.object.raw_address){
            return 'Inputted Address: <br/><i>&emsp;' + $scope.regionObject.object.raw_address + '</i><br/><br/>'
        } else {
            return '';
        }
    }
    function getGeocodedAddress(){
        var addr = 'Geocoded Address: <br/><i>&emsp;';
        if($scope.regionObject.object.geocoded_address){
            addr += $scope.regionObject.object.geocoded_address;
        } else {
            addr += $scope.regionObject.object_name;
        }
        addr += '</i><br/><br/>';
        return addr;
    }
    function getLink(){
        return '<a href="https://maps.google.com/maps?q=' + this.coords.latitude + '+' + this.coords.longitude + '" target="_blank" >View in Google</a>';
    }
    function getShowMap(){
        return vm.map.center.latitude && vm.map.center.longitude;
    }
    function setShowMap(newValues){
        var latitude = newValues[0],
            longitude = newValues[1];
        vm.map.center = {latitude: latitude, longitude: longitude};
        vm.mainMarker.coords = {latitude: latitude, longitude: longitude};
        vm.showMap = getShowMap();
    }

})
//.value('ExtraMapMarkers', typeof window.__extraMapMarkers !== 'undefined' ? window.__extraMapMarkers : []);
.factory('ExtraMapMarkers', function(){
    if(typeof window.__extraMapMarkers === 'undefined'){
        window.__extraMapMarkers = [];
    }
    return window.__extraMapMarkers;
});
