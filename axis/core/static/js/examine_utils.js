window.__extraDependencies.push('examine.regionCounters');
window.__extraDependencies.push('fileTypes');

angular.module('examine.regionCounters', [])

.controller('BadgeCounterController', function($scope, $rootScope, RegionService){
    var counter = function(){ return 0; }
    var ctrl = this;
    var types = null;
    var extra = null;
    var loaded = {};

    // Called by directive to initialize callback
    this.init = function(countGetter, regionTypes, extraOffset){
        counter = countGetter;
        types = regionTypes;
        extra = extraOffset || 0;

        // Try to find out if all types have already finished calls to the RegionLoaded event
        _.forEach(types, function(typeName){
            var regionObjects = RegionService.getRegionFromTypeName(typeName);
            if (regionObjects !== undefined) {
                var regionObject = null;
                if (_.isArray(regionObjects)) {
                    regionObject = regionObjects[0];
                } else {
                    regionObject = regionObjects;
                }
                loaded[typeName] = regionObject.controller.isDoneLoading();
            } else {
                loaded[typeName] = false;
            }
        });

        if (_.all(_.values(loaded))) {
            // Trigger once so that the count is initialized to the finished state we found.
            updateCount();
        }
    }

    // Public
    ctrl.count = null;
    ctrl.isLoaded = false;

    function updateCount(){
        ctrl.count = counter(types) + extra;
        ctrl.isLoaded = true;
    }

    $rootScope.$on("RegionLoaded", function(event, controller){
        if (types !== null && types.indexOf(controller.type_name) !== -1) {
            loaded[controller.type_name] = true;
            if (_.all(_.values(loaded))) {
                updateCount();
            }
        }
    });

    $rootScope.$on("removedRegion", function(event, regionObject){
        if (types !== null && types.indexOf(regionObject.type_name) !== -1) {
            updateCount();
        }
    });
})
.directive('badgeCounter', function(){
    return {
        restrict: 'A',
        controller: 'BadgeCounterController',
        controllerAs: 'badgeController',
        link: function(scope, element, attrs, controller){
            var counter = scope.$eval(attrs.badgeCounter);
            var types = scope.$eval(attrs.badgeCounterTypes);
            var extra = scope.$eval(attrs.badgeCounterExtra);
            controller.init(counter, types, extra);
        }
    }
})
.controller('RegionCounterController', function($scope){
    var ctrl = this;
    var counter = function(){
        return $scope.$eval(counterExpression);
    };

    ctrl.init = function(counterExpression){
        if (counterExpression) {
            counter = function(){
                var value = $scope.$eval(counterExpression);
                if (_.isFunction(value)) {
                    return value();
                }
                return value;
            }
        }
    }
    ctrl.getCount = function(){
        return counter();
    }
})
.directive('regionCounter', function(){
    return {
        restrict: 'A',
        transclude: true,
        controller: 'RegionCounterController',
        controllerAs: 'regionCounterController',
        template: '<span>[[ regionCounterController.getCount() ]] <ng-transclude></ng-transclude><ng-pluralize count="regionCounterController.getCount()" when="{\'one\': \'\', \'other\': \'s\'}"></ng-pluralize></span>',
        link: function(scope, element, attrs, controller){
            controller.init(attrs.regionCounter || null);
        }
    }
})

angular.module('fileTypes', [])
.filter('fa', function(){
    // Receives a mimetype guess, being one of the following (in order of specificity):
    //  * major mimetype, such as "text", "video", etc.
    //  * minor mimetype if the major was just "application"
    //  * just the file extension (no ".") if the mimetype guess failed entirely
    var defaultIcon = 'file-o';
    var icons = {
        'image': 'picture-o',
        'text': 'file-text-o',
        'video': 'file-video-o',
        'audio': 'file-audio-o',

        // Normally "application/" prefixed
        'pdf': 'file-pdf-o',
        'msword': 'file-word-o',
        'vnd.openxmlformats-officedocument.wordprocessingml.document': 'file-word-o',
        'vnd.ms-excel': 'file-excel-o',
        'vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'file-excel-o',
        'vnd.ms-powerpoint': 'file-powerpoint-o',
        'vnd.openxmlformats-officedocument.presentationml.presentation': 'file-powerpoint-o',
        'zip': 'file-archive-o',
        'x-rar-compressed': 'file-archive-o',

        // Types that will fail mimetype checks, so were sent as the actual extension
        'blg': 'building-o',
    }
    return function(input, forcedType){
        if (forcedType) {
            input = forcedType;
        }
        var icon = icons[input];
        if (icon === undefined) {
            icon = defaultIcon;
        }
        return icon;
    }
})
.filter('bytes', function() {
    return function(bytes, precision) {
        if (bytes === 0) {
            return '0 bytes';
        }
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) {
            return '-';
        }
        if (typeof precision === 'undefined') {
            precision = 1;
        }

        var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
            number = Math.floor(Math.log(bytes) / Math.log(1024)),
            val = (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision);

        return  (val.match(/\.0*$/) ? val.substr(0, val.indexOf('.')) : val) +  ' ' + units[number];
    }
}).filter('tel', function () {
    return function (tel) {
        if (!tel) { return ''; }

        const value = tel.toString().trim().replace(/^\+/, '');

        if (value.match(/[^0-9]/)) {
            return tel;
        }

        let country, city, number;

        switch (value.length) {
            case 10: // +1PPP####### -> C (PPP) ###-####
                country = 1;
                city = value.slice(0, 3);
                number = value.slice(3);
                break;

            case 11: // +CPPP####### -> CCC (PP) ###-####
                country = value[0];
                city = value.slice(1, 4);
                number = value.slice(4);
                break;

            case 12: // +CCCPP####### -> CCC (PP) ###-####
                country = value.slice(0, 3);
                city = value.slice(3, 5);
                number = value.slice(5);
                break;

            default:
                return tel;
        }

        if (country === '1') {
            country = "";
        }

        number = number.slice(0, 3) + '-' + number.slice(3);

        return (country + " (" + city + ") " + number).trim();
    };
});
