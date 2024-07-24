/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.region.singleRegion')
.controller('SingleRegionController', function($rootScope, $scope, $timeout, $compile, $log, $location, RegionService, UrlService, Actions, HttpQueue){
    var ctrl = this;

    //ctrl.region = {};  // just use $scope.regionObject
    ctrl.region = $scope.regionObject;
    ctrl.regionsErrors = {};
    ctrl.processing = false;
    ctrl.showLoader = true;
    ctrl.eventPrefix = 'SingleRegionLoaded:';
    ctrl.parentRegionObject = $scope.$parent.regionObject;  // Try reading outside isolated scope
    ctrl.isFormTemplateLoaded = false;
    ctrl.isDetailTemplateLoaded = false;
    ctrl.heading = {
        destination: null,
        element: null,
        scope: null
    };

    ctrl.setRegion = setRegion;  // Used in the directive
    ctrl.regionError = regionError;
    ctrl.regionSuccess = regionSuccess;
    ctrl.isDoneLoading = isDoneLoading;
    ctrl.compileHeading = compileHeading;  // region directive postLink
    ctrl.setHeadingScope = setHeadingScope;  // region directive preLink
    ctrl.setHeadingElement = setHeadingElement;  // axisRegionHeading postLink
    ctrl.primaryRegionWatcher = primaryRegionWatcher;
    ctrl.setHeadingDestination = setHeadingDestination;  // axisTransclude postLink
    ctrl.getRegionCount = getRegionCount;

    // CHILD API
    $scope.isPrimaryRegion = false;
    $scope.formTemplateLoaded = formTemplateLoaded;
    $scope.detailTemplateLoaded = detailTemplateLoaded;
    $scope.flipWatchedAttr = angular.noop;  // reset in primaryRegionWatcher, called from region link.

    init();

    function setRegion(regionObject){
        ctrl.region_template_url = regionObject.region_template_url;
        RegionService.addRegion(initRegionObject(regionObject));
        pieceLoaded();
    }
    function setHeadingDestination(element){
        if(element && element.length && angular.isElement(element)){
            ctrl.heading.destination = element;
        }
    }
    function setHeadingElement(element){
        if(element && element.length && angular.isElement(element)){
            ctrl.heading.element = element;
        }
    }
    function setHeadingScope(scope){
        if(scope && !angular.equals({}, scope)){
            ctrl.heading.scope = scope;
        }
    }
    function compileHeading(){
        if(ctrl.heading.destination){
            ctrl.heading.destination.html($compile(ctrl.heading.element)(ctrl.heading.scope));
        }
    }
    function primaryRegionWatcher(attr, flipAttr){
        /**
         * The primary-region attr determines if this gets run.
         *
         * @param attr (string) - name of attribute to watch on regionObject.object
         * @param flipAttr (string) - name of attribute to flip on $rootScope when attr changes
         *
         * We start out by assuming we're going to get a regionObject.
         * The first time we're able to do a successful lookup on a region
         * we set the `startsWithAttr` (may only be set to false) then move on.
         * When we get an update to the watcher, we check for a true ID value, then ask
         * if the regionObject started with it. If it did not start with it, change the url.
         * If it had the ID from the beginning, back off and do nothing.
         */

        ctrl.isPrimaryRegion = true;
        var startsWithAttr = true;
        function watcher(){
            // The regionObject may not be available. That's ok
            try{
                var thing = ctrl.region.object[attr];
                if(startsWithAttr) startsWithAttr = !!thing;
                return thing;
            } catch(e) {
                return undefined;
            }
        }
        function changeUrl(newId){
            // Do the work to change the URL on a save.
            var pathname = ($location.pathname || location.pathname);
            let creationPathsRe = /(add|enroll)/;
            let url;
            if (creationPathsRe.test(pathname)) {
                url = pathname.replace(creationPathsRe, `/${newId}/`);
            } else {
                url = `/${ctrl.region.type_name}/${newId}/`;
            }

            UrlService.setUpdatedLink(url);
            if(ctrl.region.helpers.page_title){
                document.title = ctrl.region.helpers.page_title;
            }
            // TODO: is there a reason for this to be here anymore?
            // now that we have all the registering function in {type}/examine.js?
            //$rootScope.$broadcast('reloadRegions', ctrl.region.type_name);
        }
        function flipWatchedAttr(){
            // Allows nested dotted access by string off of rootScope. Before the assumption was that
            // `$rootScope.creating` and `$rootScope.examineApp.creating` were the same reference.
            // They are not, so we have to allow for a dotted string lookup.
            flipAttr.split('.').reduce(function(old, curr, i, arr){
                return i + 1 == arr.length ? (old[curr] = !old[curr]) : old[curr];
            }, $rootScope);
        }

        var unwatch = $scope.$watch(watcher, function(newId){
            if(newId){
                if(!startsWithAttr){
                    changeUrl(newId);
                    if(flipAttr) {
                        $timeout(function(){
                            flipWatchedAttr();
                        }, 0)
                    }
                }
                unwatch();
            }
        })

    }
    function regionSuccess(){
        $rootScope.$broadcast(ctrl.event + ':success', ctrl.region, ctrl.$element);
    }
    function regionError(errors){
        if(angular.isObject(errors)){
            angular.forEach(errors, function(value, key){
                if(angular.isUndefined(ctrl.regionsErrors[key])) ctrl.regionsErrors[key] = [];
                if(angular.isArray(value)){
                    angular.forEach(value, function(err){
                        if(ctrl.regionsErrors[key].indexOf(err) == -1) ctrl.regionsErrors[key].push(err);
                    })
                } else {
                    if(ctrl.regionsErrors[key].indexOf(value) == -1) ctrl.regionsErrors[key].push(value);
                }
            })
        }
        $rootScope.$broadcast(ctrl.event + ':error', ctrl.region, ctrl.$element);
    }
    function detailTemplateLoaded(){
        ctrl.isDetailTemplateLoaded = true;
        $timeout(function(){
            $rootScope.$broadcast(ctrl.event + ":detailTemplateLoaded", ctrl.region, ctrl.$element);
        }, 0);
        pieceLoaded();
    }
    function formTemplateLoaded(){
        ctrl.isFormTemplateLoaded = true;
        $timeout(function(){
            $rootScope.$broadcast(ctrl.event + ":formTemplateLoaded", ctrl.region, ctrl.$element);
        }, 0);
        pieceLoaded();
    }
    function isDoneLoading(){
        var loaded = ctrl.region.type_name && (ctrl.isFormTemplateLoaded || ctrl.isDetailTemplateLoaded);
        if(loaded) ctrl.isDoneLoading = function(){return loaded};
        return loaded;
    }
    function isBusy(){
        return (ctrl.processing || ctrl.region.controller.isProcessing());
    }
    function getRegionCount(){
        return 1;
    }

    // Internal Methods
    function init(){
        errorCheck();
        $scope.options.visible_fields = $scope.visibleFields || $scope.options.visible_fields;
        angular.extend(ctrl, $scope.options);
        ctrl.event = ctrl.eventPrefix + ctrl.type_name;
        getRegionObject();
    }
    function initRegionObject(region){
        region.region_dependencies = $scope.options.region_dependencies;
        if(ctrl.parentRegionObject) region.parentRegionObject = ctrl.parentRegionObject;
        if(region.region_template_url) delete region.region_template_url;

        // NOTE: this assignment of $scope.regionObject is important
        // this is the how nested <region> directive gets access to the regionObject.
        ctrl.region = $scope.regionObject = region;
        return ctrl.region;
    }
    function errorCheck(){
        if(angular.isDefined($scope.visibleFields) && angular.isDefined($scope.options.visible_fields)){
            $log.warn("RegionSet: visible_fields is defined in both the element and options.");
        } else if(angular.isUndefined($scope.visibleFields) && angular.isUndefined($scope.options.visible_fields)){
            $log.warn("RegionSet: visible_fields is not defined on either the element or options.");
        }
    }
    function pieceLoaded(){
        if(isDoneLoading()){
            ctrl.processing = false;
            ctrl.showLoader = false;
            $timeout(function(){
                $rootScope.$broadcast("RegionLoaded", ctrl, ctrl.$element);
                $rootScope.$broadcast(ctrl.event, ctrl.region, ctrl.$element);
            }, 0);
        }
    }
    function getRegionObjectUrl(context){
        var region_endpoint_pattern = (ctrl.region ? ctrl.region.region_endpoint_pattern : $scope.options.region_endpoint_pattern);
        var url = Actions.utils.formatUrl(region_endpoint_pattern, context.object);
        // a non existent attr will be replaced with nothing causing two slashes
        // to bump each other.
        if(url.indexOf('//') > -1){
            // can comfortably take the first index of this list because we're in a single region.
            url = Actions.utils.formatUrl($scope.options.endpoints[0], context.object);
        }
        return url;
    }
    function getRegionObject(){
        var obj = {
            region_dependencies: $scope.options.region_dependencies,
            object: {},
            parentRegionSet: {
                parentRegionObject: ctrl.parentRegionObject
            }
        };
        Actions.utils.resolveDependencies(obj, false)
            .then(getRegionObjectUrl)
            .then(HttpQueue.addObjectRequest)
            .then(ctrl.setRegion);
    }
})
.directive('axisSingleRegion', function(HttpQueue, Actions){
    /**
     * Used in regular single form instance situations.
     * Straps the region fetched onto `scope.regionObject`, pass that to <axis-region/>.
     *
     * @example
     *  <axis-region region-object='regionObject' />
     */
    return {
        restrict: 'E',
        scope: {
            options: '=',
            visibleFields: '=?'
        },
        controller: 'SingleRegionController',
        controllerAs: 'regionSet',
        transclude: true,
        template: '<loading-spinner ng-if="regionSet.showLoader"></loading-spinner><div ng-transclude/><div ng-include src="regionSet.region_template_url" axis-region region-object="regionObject" ng-if="regionObject"></div>',
        link: function(scope, element, attrs, controller, transclude){
            scope.regionSet.$element = element;
            scope.regionSet.isPrimaryRegion = !!attrs.primaryRegion;
            if(attrs.primaryRegion && scope.$root.creating){
                scope.regionSet.primaryRegionWatcher(attrs.primaryRegion, attrs.primaryRegionFlip);
            }
            if(attrs.skipChildRegistration){
                scope.skipChildRegistration = scope.$eval(attrs.skipChildRegistration);
            }
        }
    }
});
