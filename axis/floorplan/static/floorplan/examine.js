angular.module('examineApp')

.controller('InputChoiceSwitcher', function($scope){
    var regions = ['remrate', 'ekotrope'];
    var firstRegion = null;
    for (var i in regions) {
        var region = regions[i];
        if ($scope.pageRegions[region] !== undefined) {
            firstRegion = region;
            break;
        }
    }
    var inputChoice = {
        type: firstRegion
    }
    $scope.inputChoice = inputChoice;
})

.controller('RemdataOnChangeController', function($scope, $http, RegionService){
    var endpointTemplates = {
        remrate: '/api/v2/floorplan/rem_data_fields/',
        ekotrope: '/api/v2/floorplan/ekotrope_fields/',
        houseplans: '/api/v2/ekotrope/houseplan/'
    };
    var toPopulate = ['name', 'number', 'square_footage'];

    function _lookupInputInfo(endpointType, triggerValue){
        if(!$scope.regionObject.object.id){
            if(triggerValue != null && hasEmptyFields()){
                var params = {
                    id: triggerValue,
                    base_name: $scope.regionObject.object.base_name
                }
                var config = {
                    'url': endpointTemplates[endpointType],
                    'method': 'GET',
                    'params': params
                };
                var floorplan = RegionService.getRegionFromTypeName('floorplan');
                floorplan.loadingInputInfo = true;
                _apiCall(config).success(updateFields);
            }
        }
    }
    function updateEkotropeHousePlanOptions(){
        var project_id = $scope.regionObject.object.ekotrope_project;
        $scope.regionObject.object.ekotrope_houseplan = null;
        _apiCall({
            url: endpointTemplates.houseplans,
            method: 'GET',
            params: {
                project: project_id
            }
        }).success(setHousePlanOptions);
    }
    function lookupEkotropeInfo(){
        var houseplan_id = $scope.regionObject.object.ekotrope_houseplan;
        _lookupInputInfo('ekotrope', houseplan_id);
    }
    function lookupRemrateInfo(){
        var simulation_id = $scope.regionObject.object.remrate_target;
        _lookupInputInfo('remrate', simulation_id);
    }

    function hasEmptyFields(){
        var object = $scope.regionObject.object;
        var hasEmpty = false;
        for(var i in toPopulate){
            var value = object[toPopulate[i]];
            hasEmpty = hasEmpty || (value == null || value === "");
        }
        return hasEmpty;
    }
    function _apiCall(config){
        return $http(config).error(function(data, code){
            console.log(data, code);
        });
    }
    function updateFields(data){
        var floorplan = RegionService.getRegionFromTypeName('floorplan');
        var object = floorplan.object;
        for(var i in toPopulate){
            var field = toPopulate[i];
            if(!object[field]){
                object[field] = data[field];
            }
        }
        floorplan.loadingInputInfo = false;
    }
    function setHousePlanOptions(data){
        var element = $scope.region.axisFields.ekotrope_houseplan;
        var elementScope = angular.element(element.find('[multi-select-helper]')).scope();
        var choices = $scope.regionObject.fields.ekotrope_houseplan.widget.choices;
        choices.length = 0;
        for (var i in data.results) {
            var item = [
                data.results[i].id,
                data.results[i].name
            ]
            choices.push(item);
        }
    }

    var fn = {
        updateEkotropeHousePlanOptions: updateEkotropeHousePlanOptions,
        lookupRemrateInfo: lookupRemrateInfo,
        lookupEkotropeInfo: lookupEkotropeInfo
    };
    angular.extend($scope, fn);
})

.controller('ValidateRemVsBlgController', function($scope, $http){
    $scope.$watchGroup(['regionObject.object.remrate_target', 'regionObject.object.remrate_data_file_raw'], function(nV, oV){
        if(_.every(nV)){
            var config = {
                'url': '/api/v2/remrate/' + nV[0] + '/validate/',
                'method': 'POST',
                'data': {
                    'file': nV[1]
                }
            };
            $http(config).success(function(data){
                $scope.validation_data = data;
                $scope.data_has_mismatches = Object.keys($scope.validation_data).length != 0;
            }).error(function(data, code){
                console.warn(data, code);
            });
        }
    });
    $scope.validationClass = function(obj){
        return obj.matches ? 'text-success' : {
            'info': 'text-info',
            'warning': 'text-warning',
            'error': 'text-danger'
        }[obj.level];
    }
})
.directive('validateRemVsBlg', function(){
    return {
        restrict: 'A',
        controller: 'ValidateRemVsBlgController'
    }
})
.directive('updateRemdataOnChange', function(){
    return {
        restrict: 'A',
        controller: 'RemdataOnChangeController'
    }
})
.run(function($rootScope, Actions, RegionService){
    var object_id = window.__primary_object_id;

    function reloadRelationshipSidebar(regionObject){
        var floorplanRegion = RegionService.getRegionFromTypeName('floorplan');
        build_relationship_sidebar(null, floorplanRegion);
        return regionObject;
    }

    function reloadSystems(regionObject){
        var systemRegions = RegionService.getRegionFromTypeName('floorplan_systems');
        systemRegions.controller.handleAction('reload');
    }

    Actions.addPostMethodToType('save', ['floorplan', 'floorplan_relationships'], reloadRelationshipSidebar);
    Actions.addPostMethodToType('delete', ['floorplan', 'floorplan_relationships'], reloadRelationshipSidebar);
    Actions.addPostMethodToType('save', 'floorplan', reloadSystems);

    Actions.addPreMethodToType('save', 'floorplan_documents', function(regionObject){
        regionObject.object.object_id = object_id;
    });

    $rootScope.$on("addedRegion:floorplan_documents", function(e, regionObject){
        regionObject.region_dependencies = {};
    });

    if(angular.isDefined(window.build_relationship_sidebar)){
        $rootScope.$on('SingleRegionLoaded:floorplan:detailTemplateLoaded', build_relationship_sidebar);
    }
})
.factory('Compare', function(){
    return {
        'show_sim': true,
        'show_blg': true,
        'hide_matching': false
    };
})
.controller('CompareController', function($scope, $http, Compare, RegionService){
    var ctrl = this;
    ctrl.Compare = Compare;
    var floorplan = RegionService.getRegionFromTypeName('floorplan');
    $http.get('/api/v3/simulations/'+floorplan.object.simulation+'/blg_compare/').then(function(response){
        ctrl.errors = response.data.errors;
        ctrl.warnings = response.data.warnings;
        ctrl.ignored = response.data.ignored;
        ctrl.summary = response.data.summary;
    }, function(response){
        ctrl.error = response.data;
    });

})
.directive('valueOutput', function(){
    return {
        scope: {
            key: '=',
            value: '=',
        },
        controller: function(Compare){
            var ctrl = this;

            var backgroundClasses = {
                'info': 'info',
                'error': 'danger',
                'warning': 'warning',
            }

            ctrl.Compare = Compare;
            ctrl.backGroundClass = 'alert-' + (ctrl.value.matches ? 'success' : backgroundClasses[ctrl.value.level]);
        },
        controllerAs: 'ctrl',
        bindToController: true,
        template: '' +
        '<div class="alert alert-sm" ng-class="::[ctrl.backGroundClass]" ng-if="!(ctrl.Compare.hide_matching && ctrl.value.matches)">' +
            '<label ng-bind="::ctrl.key"></label><br>' +
            '<span ng-if="::ctrl.value.name">Validation Name: <span ng-bind="::(ctrl.value.name | json)"></span><br/></span>' +
            '<span ng-show="ctrl.Compare.show_sim">sim: <span ng-bind="::(ctrl.value.sim | json)"></span><br></span>' +
            '<span ng-show="ctrl.Compare.show_blg">blg: <span ng-bind="::(ctrl.value.blg | json)"></span></span>' +
        '</div>'
    }
})
.directive('displayOutput', function(){
    return {
        scope: {
            object: '='
        },
        controller: function(){
            var ctrl = this;
            var textClasses = {
                'info': 'info',
                'error': 'danger',
                'warning': 'warning'
            }

            ctrl.values = _.reject(ctrl.object, function(o){
                return o.matches === undefined;
            });
            ctrl.getBackground = function(obj){
                return 'text-' + (obj.matches ? 'success' : textClasses[obj.level]);
            }
            ctrl.getIcon = function(obj){
                obj.matches ? 'fa-check' : 'fa-times';
            }

        },
        bindToController: true,
        controllerAs: 'ctrl',
        template: '<i class="fa fa-fw" ng-class="::[ctrl.getBackground(result), ctrl.getIcon(result)]" ng-repeat="result in ::ctrl.values track by $index"></i>'
    }
})
.directive('objectOutput', function($compile){
    return {
        scope: {
            object: '='
        },
        controller: function(){
            var ctrl = this;

            ctrl.isArray = _.isArray;
            ctrl.isObject = _.isPlainObject;
            ctrl.isValue = function(obj){ return _.has(obj, 'matches'); }

            ctrl.VALUE = 2;
            ctrl.ARRAY = 1;
            ctrl.OBJECT = 0;

            ctrl.checker = function(obj){ return ctrl.isValue(obj) ? ctrl.VALUE : ctrl.isArray(obj) ? ctrl.ARRAY : ctrl.OBJECT; };
            ctrl.down = ctrl.checker(ctrl.object);
            ctrl.cast = _.memoize(function(obj){
                return _.indexBy(obj, function(obj, index, array){
                    return index;
                });
            });
        },
        controllerAs: 'ctrl',
        bindToController: true,
        template: '' +
        '<div class="row">' +
            '<div ng-repeat="(key, value) in ::ctrl.object">' +
                '<div class="col-md-4" ng-if="::(ctrl.checker(value) === ctrl.VALUE)">' +
                    '<value-output key="::key" value="::value"></value-output>' +
                '</div>' +
                '<div class="col-md-12" style="margin-bottom: 20px;" ng-if="::(ctrl.checker(value) !== ctrl.VALUE)">' +
                    '<div class="row">' +
                        '<div class="col-md-12">' +
                            '<accordion-group>' +
                                '<accordion-heading><span ng-bind="::key"></span> <display-output object="::value"></display-output></accordion-heading>' +
                                '<object-output object="::(ctrl.checker(value) === ctrl.ARRAY ? ctrl.cast(value) : value)"></object-output>' +
                            '</accordion-group>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>',
        compile: function(element){
            var contents = element.contents().remove();
            var contentsLinker;

            return function(scope, iElement){
                if(angular.isUndefined(contentsLinker)){
                    contentsLinker = $compile(contents);
                }
                contentsLinker(scope, function(clonedElement){
                    iElement.append(clonedElement);
                });
            }
        }
    }
})
