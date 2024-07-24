angular.module('axis')
.controller('HomeTaskFormController', function($scope, $rootScope, $http, $timeout, $window, Actions){
    Actions.addPreMethodToType('save', 'home_task', function (regionObject) {
        if (regionObject.object['date'] && regionObject.object['time']) {
            let [hours, minutes, ] = regionObject.object["time"].split(':')
            let datetime = new Date(regionObject.object['date']);
            datetime.setHours(hours, minutes, 0);
            regionObject.object['datetime'] = moment(datetime).format('YYYY-MM-DD HH:mm');
        }
        $rootScope.regionObject = regionObject;

        return regionObject;
    });
})
.controller('UserTaskFormController', function($scope, $rootScope, $http, $timeout, $window, Actions){
    Actions.addPreMethodToType('save', 'user_task', function (regionObject) {
        if (regionObject.object['date'] && regionObject.object['time']) {
            let [hours, minutes, ] = regionObject.object["time"].split(':')
            let datetime = new Date(regionObject.object['date']);
            datetime.setHours(hours, minutes, 0);
            regionObject.object['datetime'] = moment(datetime).format('YYYY-MM-DD HH:mm');
        }
        console.log(regionObject.object)
        $rootScope.regionObject = regionObject;

        return regionObject;
    });
})