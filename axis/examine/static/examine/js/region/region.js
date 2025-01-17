/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.region.region')
.controller('RegionController', function($rootScope, $scope, $timeout, $q, $log, Actions, RegionService, ExamineSettings){
    var ctrl = this;

    ctrl.getRegionObject = function() { return $scope.regionObject; }
    ctrl.children = [];
    ctrl.axisFields = {};
    ctrl.activeState = $scope.regionObject.default_instruction || 'default';
    // ctrl.processing = null;
    ctrl.processingInstructions = [];
    ctrl.hasEdited = false;

    ctrl.error = error; // what type of error?
    ctrl.reset = reset; // TODO: better name.
    ctrl.editing = editing;
    ctrl.success = success; // what type of success?
    ctrl.isProcessing = isProcessing;
    ctrl.addProcessingStatus = addProcessingStatus;
    ctrl.clearProcessingStatus = clearProcessingStatus;
    ctrl.removeRegion = getRemoveRegion();
    ctrl.handleAction = handleAction;
    ctrl.shouldShowCommitAction = shouldShowCommitAction;
    ctrl.isCommitAction = isCommitAction;

    $rootScope.$on('reloadRegions', reloadRegionListener);

    init();

    function editing(){
        var editing = ctrl.activeState === 'edit';
        ctrl.hasEdited = ctrl.hasEdited || editing;
        return editing;
    }
    function handleAction(action){
        return Actions.callMethod(action, $scope.regionObject).then(getActionCallback(action));
    }
    function reset(){
        angular.copy($scope.regionObject._masterForm, $scope.regionObject.object);
    }
    function success(message){
        $scope.regionObject.errors = {};
        $scope.timedClass('success');
        $scope.regionSet.regionSuccess(message, ctrl);
    }
    function error(message){
        if(!angular.isObject(message) || angular.isArray(message)) {
            message = {'non_field_errors': angular.isArray(message) ? message : [message]};
        }
        if(angular.isDefined(message.__all__)) message = {'non_field_errors': message.__all__};

        angular.copy(message, $scope.regionObject.errors);
        $scope.timedClass('error');
        $scope.regionSet.regionError(message, ctrl);
    }
    function reloadRegionListener(event, firingType){
        if($scope.regionObject.type_name != firingType && !$scope.regionSet.processing){
            Actions.callMethod('reload', $scope.regionObject);
        }
    }
    function isProcessing(methodName){
        if (methodName === undefined){
            return ctrl.processingInstructions.length > 0;
        } else if (_.isArray(methodName)){
            // Dropdown items
            var containsInstruction = false;
            _.map(methodName, function(itemMethodName){
                if (itemMethodName !== null && itemMethodName.instruction) {
                    itemMethodName = itemMethodName.instruction;
                }
                if (itemMethodName !== null && _.contains(ctrl.processingInstructions, itemMethodName)) {
                    containsInstruction = true;
                }
            });
            return containsInstruction;
        }
        return _.contains(ctrl.processingInstructions, methodName);
    }
    function addProcessingStatus(methodName){
        // if (methodName === undefined){
        //     methodName = true;  // generic flag
        // }
        $log.debug("Region busy status added", methodName, "to", ctrl.processingInstructions);
        ctrl.processingInstructions.push(methodName);
        ctrl.processing = methodName;
    }
    function clearProcessingStatus(methodName){
        if (methodName === undefined){
            ctrl.processingInstructions = [];
            $log.debug("Region cleared ALL");
        } else {
            _.pull(ctrl.processingInstructions, methodName);
            $log.debug("Region cleared", methodName, "(Remaining:", ctrl.processingInstructions, ")");
        }
    }
    function shouldShowCommitAction(){
        var primaryRegionObject = RegionService.getRegionFromTypeName(ExamineSettings.page);
        if (primaryRegionObject !== undefined) {
            if (ctrl.type_name == primaryRegionObject.type_name) {
                return true;
            }
            return primaryRegionObject.object.id !== null;
        }
        return true;
    }
    function isCommitAction(actionObject){
        var instruction = angular.isObject(actionObject) ? actionObject.instruction : actionObject;
        return (instruction === $scope.regionObject.commit_instruction);
    }

    // Internal Methods
    function init(){
        angular.extend(ctrl, $scope.regionObject.additionalScope);
        ctrl.type_name = $scope.regionObject.type_name;
        clearProcessingStatus();
        initRegionObject();
        liftInitialFieldValues();
    }
    function initRegionObject(){
        $scope.regionObject.errors = {};
        $scope.regionObject.controller = ctrl;
        $scope.regionObject._masterForm = angular.copy($scope.regionObject.object);
        $scope.regionObject.object_endpoint_pattern = $scope.options.object_endpoint_pattern;
    }
    function liftInitialFieldValues(){
        angular.forEach($scope.regionObject.fields, function(field){
            if(field.value){
                $scope.regionObject.object[field.field_name] = field.value;
            }
        })
    }
    function saveChildren(){
        var childrenSaves = [];

        angular.forEach(ctrl.children, function(child, index){
            if (child.commit_instruction && child.controller.editing() && !child.passive_machinery) {
                var save = Actions.callMethod(child.commit_instruction, child).then(function(){
                    Actions.callMethod('exit', child);
                }).finally(function(){
                    // clear the commit instruction in case it failed
                    child.controller.clearProcessingStatus(child.commit_instruction);
                    // clear the waiting status that may have been added through saveAll
                    child.controller.clearProcessingStatus('waiting');
                });
                childrenSaves.push(save);
            }
        });

        return $q.all(childrenSaves);
    }
    function getActionCallback(action){
        // Decides if it needs to save the children first, then return to default state
        var fn = angular.identity;
        var saveAction = ctrl.isCommitAction(action);

        if(action && saveAction && ctrl.children.length){
            fn = saveChildren;
        }

        return function returnToDefault(){
            return $q.when(fn()).then(function(){
                if(saveAction){
                    return Actions.callMethod('exit', $scope.regionObject);
                }
            });
            // TODO: handle errors for regions hereish?
        }
    }
    function getRemoveRegion(){
        return $scope.regionSet.removeRegion || angular.noop;
    }
})
.directive('axisRegion', function($compile, $q, HttpQueue, $timeout, RegionService){
    /**
     * Used inside a <axis-single-region/> or <axis-region-set/> for
     * rendering a detail and form section of a region.
     *
     * If not using default template, classes `.detail-content` and `.form-content` are
     * used to determine where to put respective templates.
     *
     * @requires: regionObject
     * @example:
     *      <axis-region region-object='{... object ...}'>
     *          <div class='detail-content'></div>
     *          <div class='form-content'></div>
     *      </axis-region>
     */
    return {
        restrict: 'EA',
        require: '^?axisSingleRegion',
        scope: true,
        controller: 'RegionController',
        controllerAs: 'region',
        template: '<span ng-include src="regionObject.region_template_url" ng-if="regionObject.region_template_url && !regionSet.region_template_url" ng-include-replace></span>',
        link: {
            pre: function preLink(scope, element, attrs, parentController){
                if(parentController){
                    parentController.setHeadingScope(scope);
                }
            },
            post: function postLink(scope, element, attrs, parentController){
                scope.regionObject.$element = element;
                scope.regionObject.parentRegionSet = scope.regionSet;
                element.attr('type-name', scope.regionObject.type_name);
                if(parentController){
                    parentController.compileHeading();
                }

                scope.timedClass = function(klass, duration){
                    element.addClass(klass);
                    $timeout(function(){
                        element.removeClass(klass);
                    }, duration || 3000);
                };

                if(scope.regionObject.parentRegionObject && !scope.skipChildRegistration){
                    RegionService.registerChildRegion(scope.regionObject.parentRegionObject, scope.regionObject);
                }
            }
        }
    }
})
.directive('detailContent', function($compile, HttpQueue){
    return {
        restrict: 'EA',
        link: function(scope, element, attrs){
            var unwatch;
            unwatch = scope.$watch(function(){
                return scope.region.editing();
            }, function(val) {
                if (!val) {
                    HttpQueue.addTemplateRequest(scope.regionObject.detail_template_url).then(function(template) {
                        var method = attrs.detailContent == 'replace' ? 'replaceWith' : 'html';
                        element[method]($compile(template)(scope));
                        scope.detailTemplateLoaded(scope.regionObject, element);
                        unwatch();
                    });
                }
            });
        }
    }
})
.directive('formContent', function($compile, HttpQueue){
    return {
        restrict: 'EA',
        link: function(scope, element, attrs){
            var method = attrs.formContent == 'replace' ? 'replaceWith' : 'html';
            var compiled = null;

            function _compile() {
                return HttpQueue.addTemplateRequest(scope.regionObject.form_template_url).then(function(template){
                    if (compiled === null) {
                        compiled = $compile(template);
                    }
                });
            }

            if(scope.regionObject.form_template_url){
                var compileQ = _compile();
                var unwatch;
                unwatch = scope.$watch(function(){
                    return scope.region.editing();
                }, function(val){
                    if(val){
                        compileQ.then(function(){
                            element[method](compiled(scope));
                            scope.formTemplateLoaded(scope.regionObject, element);
                            unwatch();
                        });
                    }
                })
            }
        }
    }
});
