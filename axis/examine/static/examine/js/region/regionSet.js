/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.region.regionSet')
.controller('RegionSetController', function($rootScope, $scope, $timeout, $compile, $log, HttpQueue, RegionService, Actions){
    /**
     * NOTE: pieceLoaded() and isDoneLoading() use a counter because we want to know when a
     *       regions compilation process is done, including loading all necessary templates.
     *       The Region is added to ctrl.regions long before anything is finished loading.
     */
    var ctrl = this;

    var fetched_endpoints = [];

    ctrl.regions = [];
    ctrl.processing = false;
    ctrl.regionsErrors = {};
    ctrl.initialLoad = false;
    ctrl.eventPrefix = 'RegionSetLoaded:';
    ctrl.detailTemplatesCount = 0;
    ctrl.formTemplatesCount = 0;
    ctrl.parentRegionObject = $scope.$parent.regionObject;  // Try reading outside isolated scope

    ctrl.addRegion = addRegion;
    ctrl.hotUpdate = hotUpdate;
    ctrl.regionError = regionError;
    ctrl.removeRegion = removeRegion;
    ctrl.regionSuccess = regionSuccess;
    ctrl.isDoneLoading = isDoneLoading;
    ctrl.fetchNewRegion = fetchNewRegion;
    ctrl.getRegionCount = getRegionCount;
    ctrl.getRegion = getRegion;
    ctrl.isFull = isFull;

    // CHILD API
    $scope.formTemplateLoaded = formTemplateLoaded;
    $scope.detailTemplateLoaded = detailTemplateLoaded;

    init();

    function addRegion(region){
        ctrl.regions.push(RegionService.addRegion(initRegionObject(region)));
        pieceLoaded();
        return region;
    }
    function removeRegion(region){
        var index = ctrl.regions.indexOf(region);
        ctrl.regions.splice(index, 1);
        if(ctrl.parentRegionObject){
            var parentIndex = ctrl.parentRegionObject.controller.children.indexOf(region);
            ctrl.parentRegionObject.controller.children.splice(parentIndex, 1);
        }
    }
    function fetchNewRegion(additionalScope){
        if (isFull()) {
            return;
        }
        ctrl.processing = true;
        var depsObject = {region_dependencies: ctrl.region_dependencies, object: {}};
        return Actions.utils.resolveDependencies(depsObject, false).then(function(context){
            return Actions.utils.formatUrl(ctrl.new_region_url, context.object, ctrl.type_name);
        }).then(function(url){
            return HttpQueue.addObjectRequest(url, additionalScope);
        }).then(ctrl.addRegion).finally(function(){
            ctrl.processing = false;
        });
    }
    function regionSuccess(message, region){
        ctrl.regionsErrors = {};
        $rootScope.$broadcast(ctrl.event + ':success', region.getRegionObject(), ctrl.$element);
    }
    function regionError(errors, region){
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
        $rootScope.$broadcast(ctrl.event + ':error', region.getRegionObject(), ctrl.$element);
    }
    function detailTemplateLoaded(region, element){
        ctrl.detailTemplatesCount++;
        $timeout(function(){
            $rootScope.$broadcast(ctrl.event + ':detailTemplateLoaded', region, element);
        });
        pieceLoaded();
    }
    function formTemplateLoaded(region, element){
        ctrl.formTemplatesCount++;
        $timeout(function(){
            $rootScope.$broadcast(ctrl.event + ':formTemplateLoaded', region, element);
        });
        pieceLoaded();
    }
    function isDoneLoading(){
        // Check >= because new additions will change the length of the regions, but not the initial
        // endpoints.
        var len = ctrl.endpoints.length;
        var initialLoad = ctrl.regions.length >= len           &&
                          (ctrl.detailTemplatesCount >= len    ||
                           ctrl.formTemplatesCount >= len);

        // once this is true we want to memoize it.
        if(initialLoad) ctrl.isDoneLoading = function(){ return initialLoad };
        return initialLoad;
    }
    function isBusy(){
        var processingFlags = _.map(ctrl.regions, function(regionObject){
            return regionObject.controller.isProcessing();
        });
        return (ctrl.processing || _.compact(processingFlags).length > 0);
    }
    function getRegionCount(){
        return ctrl.regions.length;
    }
    function hotUpdate(){
        $scope.$watch('options.endpoints', function(newVal, oldVal){
            if(!angular.equals(newVal, oldVal)){
                var obj = {
                    region_dependencies: $scope.options.region_dependencies,
                    object: {},
                    parentRegionSet: {
                        parentRegionObject: ctrl.parentRegionObject
                    }
                };
                Actions.utils.resolveDependencies(obj, false)
                .then(function(context){
                    angular.forEach(newVal, function(endpoint){
                        var url = Actions.utils.formatUrl(endpoint, context.object);
                        if(fetched_endpoints.indexOf(url) == -1){
                            getRegion(url);
                        }
                    });
                })
            }

        });
    }
    function isFull(){
        if (ctrl.max_regions === null) {
            return false;
        }
        return (ctrl.regions.length >= ctrl.max_regions);
    }

    // Internal Methods
    function init(){
        errorCheck();
        $scope.options.visible_fields = $scope.visibleFields || $scope.options.visible_fields;
        angular.extend(ctrl, $scope.options);
        ctrl.event = ctrl.eventPrefix + ctrl.type_name;
        // trigger the check for everything is loaded
        // if there is nothing to load.
        ctrl.endpoints.length == 0 ? pieceLoaded() : getRegions();

    }
    function initRegionObject(region){
        region.region_dependencies = ctrl.region_dependencies;
        if(ctrl.parentRegionObject) region.parentRegionObject = ctrl.parentRegionObject;
        region.parentRegionController = ctrl;
        return region
    }
    function errorCheck(){
        // some requirement checks first
        if(angular.isUndefined($scope.options.endpoints)){
            throw new Error('RegionSets require endpoints to be defined');
        }

        if(angular.isUndefined($scope.options.new_region_url)){
            $log.warn('RegionSet does not have new_region_endpoint defined');
        }

        if(angular.isDefined($scope.visibleFields) && angular.isDefined($scope.options.visible_fields)){
            $log.warn("RegionSet: visible_fields is defined in both the element and options.");
        } else if(angular.isUndefined($scope.visibleFields) && angular.isUndefined($scope.options.visible_fields)){
            $log.warn("RegionSet: visible_fields is not defined on either the element or options.");
        }
    }
    function pieceLoaded(){
        // TODO: still not happy with this name.
        // Gets called when the following are loaded
        //  [regions, detail templates, form templates]
        // So we can fire the event as soon as possible.
        if(isDoneLoading()){
            ctrl.processing = false;
            $timeout(function(){
                $rootScope.$broadcast("RegionLoaded", ctrl, ctrl.$element);
                $rootScope.$broadcast(ctrl.event, ctrl.regions, ctrl.$element);
            });
        }
    }
    function getRegions(){
        var obj = {
            region_dependencies: $scope.options.region_dependencies,
            object: {},
            parentRegionSet: {
                parentRegionObject: ctrl.parentRegionObject
            }
        };
        Actions.utils.resolveDependencies(obj, false)
        .then(function(context){
            angular.forEach(ctrl.endpoints, function(endpoint){
                var url  = Actions.utils.formatUrl(endpoint, context.object);
                getRegion(url);
            })
        });
    }
    function getRegion(url){
        fetched_endpoints.push(url);
        HttpQueue.addObjectRequest(url).then(ctrl.addRegion);
    }
})
.directive('axisRegionSet', function($q, HttpQueue){
    /**
     * Used in Formset type situations.
     *
     * In the region template make <axis-region/> by ngRepeating over
     * `scope.regions` and passing the object.
     *
     * @example
     *  <axis-region region-object='object' ng-repeat='object in regions' />
     */
    return {
        restrict: 'E',
        scope: {
            options: '=',
            visibleFields: '=?'
        },
        controller: 'RegionSetController',
        controllerAs: 'regionSet',
        template: '<div class="region-set" ng-include src="regionSet.regionset_template_url"></div>',
        link: function(scope, element, attrs){
            scope.regionSet.$element = element;

            if(angular.isDefined(attrs.hotUpdate)){
                scope.regionSet.hotUpdate();
            }

            if(angular.isDefined(attrs.skipChildRegistration)){
                scope.skipChildRegistration = scope.$eval(attrs.skipChildRegistration)
            }
        }
    }
})
.directive('regionSetNonFieldErrors', function($sce){
    return {
        restrict: 'EA',
        template: '<ul class="text-danger" ng-if="regionSet.regionsErrors.non_field_errors"> <li ng-repeat="message in regionSet.regionsErrors.non_field_errors"><span ng-bind-html="message | trustAsHtml"></span></li> </ul>'
    }
});
