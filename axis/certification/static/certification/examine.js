angular.module('examineApp')

.service('ActionRouter', function($state, $timeout, $state, RegionService, Actions){
    init();

    // This should be promoted to the Actions service as a matter of design convenience
    return {
        route: routeActionLink
    }

    function init() {
        // Bind 'reveal' events for known UI patterns
        // Don't stop propagation in any of these or else the element may not be completely revealed

        function _focus(element) {
            $(element).focus();
        }

        $('body').on('reveal', 'input', function(){
            $(this).focus();
        });

        $('body').on('reveal', '[data-switcher]', function revealFauxSwitcherPane(event, targetElement, selector){
            var pane = $(this);
            var category = pane.attr('data-switcher');
            var clicker = pane.closest('.data-browser').find('.nav [data-switcher="'+category+'"]');

            clicker.click();
            _focus(targetElement);
        })

        $('body').on('reveal', '.tab-pane', function revealTabPane(event, targetElement, selector){
            var pane = $(this);
            var tabIndex = pane.index();

            // Go up to outer container (maybe an outer tab-pane wrapping this one)
            var container = pane.parent().closest('.tab-pane,body');

            // Follow it back down to find the tab strip
            var clicker = container.find('.nav-tabs').find('li a').eq(tabIndex);
            clicker.click();
            _focus(targetElement);
        });
    }

    function routeActionLink(regionObject, url) {
        // NOTE: This version of this function can't target an arbitrary remote region

        // Try to route a url locally if it's in one of the forms:
        // * #instruction-edit
        // * #instruction-edit:selectorpath
        // Where 'selectorpath' targets an element to be revealed (through tabs, panels, etc)
        var bits = url.split('#instruction-', 2);
        var baseUrl = bits[0];
        var regionInstruction = bits[1];

        if (!regionInstruction) {
            // No special behavior; try to pass through

            if (url.indexOf('#/') === 0) {
                $state.go(url.substr(2).replace('/', '.'));
                return;
            } else {
                // No special treatment
                window.location = url;
                return;
            }
        }

        // Assume local instruction first
        var targetRegionObject = regionObject;

        var instructionBits = regionInstruction.split(':', 2);
        var instruction = instructionBits[0];
        var selector = instructionBits[1];

        Actions.callMethod(instruction, regionObject, function(){
            // Default to using the whole region as target element to reveal
            var targetElement = $(regionObject.$element);

            if (selector !== undefined) {
                targetElement = $(selector);
            }

            targetElement.trigger('reveal', [targetElement, selector]);
        });

        return true;
    }
})

.controller('CertifiableObjectController', function($scope){
    var ctrl = this;
    var regionObject = $scope.regionObject;

    ctrl.walkParents = walkParents;

    function walkParents(){
        var parents = [];
        var item = regionObject.object;
        while ((item = item.parent_info)) {
            parents.push(item);
        }
        return parents;
    }
})

.controller('WorkflowStatusController', function($scope, $http){
    var ctrl = this;
    var regionObject = $scope.regionObject;

    var requirements = {
        data: {},
        loading: false,
        reload: function(){
            $http.get(regionObject.helpers.requirements_url).success(function(data){
                requirements.loading = true;
                requirements.data = data;
            }).then(function(){
                requirements.loading = false;
            });
        }
    }

    function init(){
        if (regionObject.object.id) {
            ctrl.requirements.reload();
        }
    }

    ctrl.requirements = requirements;
    ctrl.showNotes = false;  // Flag to help us fake a global tab-activator panel

    init();
})

.controller('FauxTabSwitcherController', function($scope){
    var ctrl = this;
    var regionObject = $scope.regionObject;

    ctrl.getActive = function(){
        return regionObject._panel;
    }
    ctrl.setActive = function(panelId){
        regionObject._panel = panelId;

        // (De)activate external region notes panel
        $scope.statusCtrl.showNotes = (panelId == 'notes');
    }

})
.directive('fauxTabSwitcher', function(){
    return {
        restrict: 'A',
        controllerAs: 'switcherCtrl',
        controller: 'FauxTabSwitcherController'
    }
})

.directive('programProgressBar', function(){
    return {
        restrict: 'E',
        require: '^axisRegion',
        templateUrl: '/examine/certification/requirements_progress_bar.html'
    }
})

.controller('ProgramProgressList', function($scope, $sce, ActionRouter){
    var ctrl = this;
    ctrl.trustAsHtml = $sce.trustAsHtml;
    ctrl.routeRequirementLink = function route(url){
        return ActionRouter.route($scope.regionObject, url);
    };

    ctrl.showingCompleted = false;
    ctrl.toggleCompleted = toggleCompleted;

    function toggleCompleted(){
        ctrl.showingCompleted = !ctrl.showingCompleted;
    }
})
.directive('programProgressList', function(){
    return {
        restrict: 'E',
        require: '^axisRegion',
        controllerAs: 'progressCtrl',
        controller: 'ProgramProgressList',
        templateUrl: '/examine/certification/requirements_list.html'
    }
})

.directive("compileHtml", function($parse, $sce, $compile) {
    return {
        restrict: "A",
        link: function(scope, element, attributes) {
            var expression = $parse(attributes.compileHtml);

            var getResult = function() {
                return expression(scope);
            };

            scope.$watch(getResult, function(newValue) {
                element.append($compile(newValue)(scope));
            });
        }
    }
})

// .controller('StubNewCertifiableObjectModalController', function($scope, $modalInstance, regionObject, extraData, saveUrl){
//     var vm = this;
//     $scope.regionObject = vm.regionObject = regionObject;
//     $scope.extraData = vm.extraData = extraData;
//     vm.ok = function(){
//         $http.post(saveUrl, regionObject.object).then(function(response){
//             $modalInstance.close(vm.regionObject);
//         });
//     };
//     vm.cancel = function(){
//         $modalInstance.dismiss('cancel');
//     };
// })

.run(function($rootScope, $http, $modal, Actions, RegionService){
    var lazyCallMethod = _.debounce(Actions.callMethod, 1000, {leading: true, trailing: false});

    $rootScope.$on('RegionSetLoaded:workflowstatus:detailTemplateLoaded', selectFirstDataTab);
    $rootScope.$on('RegionSetLoaded:workflowstatus:error', highlightTabErrors);
    $rootScope.$on('RegionSetLoaded:workflowstatus:success', clearTabErrors);
    Actions.addMethod('noop', angular.noop);
    Actions.addMethod('change_state', requestStateTransition);
    Actions.addPostMethodToType('save', 'certifiableobject', updateAddChildButton);
    Actions.addPostMethodToType('save', 'certifiableobject', reloadRequirements);
    Actions.addPostMethodToType('save', 'workflowstatus', reloadRequirements);
    Actions.addPostMethodToType('change_state', 'workflowstatus', reloadRequirements);
    // Actions.addMethod('new_certifiable_object', createNewCertifiableObject)

    var tabBadgeTemplate = $('<span class="label label-danger"></span>');

    function selectFirstDataTab(event, regionObject, element) {
        // This only needs to be done on the detail loader because the state is sticky across both
        // detail and form modes.
        element.find('.data-browser .nav a.btn:first-child').click();
    }
    function clearTabErrors(event, regionObject, element) {
        regionObject.$element.find('.data-browser .nav [data-switcher] .label').remove();
    }
    function highlightTabErrors(event, regionObject, element) {
        clearTabErrors(event, regionObject, element);
        angular.forEach(Object.keys(regionObject.errors), function(fieldName){
            var el = regionObject.$element.find('[name="'+fieldName+'"]');
            var category = el.closest('[data-switcher]').attr('data-switcher');
            var fauxTabButton = el.closest('.data-browser').find('.nav [data-switcher="'+category+'"]');
            var badge = fauxTabButton.find('.label');
            if (badge.length == 0) {
                badge = tabBadgeTemplate.clone();
                fauxTabButton.append(badge);
            }
            var numErrors = (parseInt(badge.text()) || 0);
            badge.text(numErrors + 1);
        });
    }
    function requestStateTransition(regionObject, action) {
        var data = {
            'id': regionObject.object.id,
            'transition': action.transition
        };
        return $http.patch(regionObject.helpers.state_transition_url, data).then(function(){
            lazyCallMethod('reload', regionObject);
            regionObject.controller.success();
            return regionObject;
        }, function(data){
            regionObject.controller.error(data.data);
        });
    }
    function updateAddChildButton(regionObject){
        var button = $('#add-child-button');
        if (button.length) {
            var href = button.attr('href');
            button.attr('href', href.replace(/\/0\//, '/'+regionObject.object.id+'/'));
        }
    }
    // function createNewCertifiableObject(regionObject, action) {
    //     var resolves = {
    //         regionObject: function(){ return regionObject },
    //         extraData: function(){ {object_type: action.objectType} }
    //         saveUrl: function(){ action.saveUrl }
    //     }
    //     var modal = $modal.open({
    //         templateUrl: 'examine/certification/certifiable_object_form_modal.html',
    //         resolve: resolves,
    //         controller: 'StubNewCertifiableObjectModalController',
    //         controllerAs: 'vm',
    //         size: 'lg'
    //     });
    //
    //     return modal.result.then(function(){
    //         return methodReload(regionObject);
    //     });
    //
    //     action.objectType
    //     console.log(regionObject, action);
    // }
    function reloadRequirements(regionObject) {
        var objects = null;
        if (regionObject.type_name == 'workflowstatus') {
            objects = [regionObject];
        } else if (regionObject.type_name == "certifiableobject") {
            // Set to the scopes of all workflowstatus items
            var regions = RegionService.getRegionFromTypeName('workflowstatus');
            if (_.isArray(regions)) {
                objects = regions;
            } else if (regions !== undefined) {
                objects = [regions];
            }
        } else {
            console.error("Can't reload requirements from region type:", regionObject.type_name);
            return;
        }
        for (var i in objects) {
            objects[i].$element.scope().statusCtrl.requirements.reload();
        }
    }
})

.run(function trc($http, Actions){
    var lazyCallMethod = _.debounce(Actions.callMethod, 1000, {leading: true, trailing: false});

    Actions.addMethod('trc_escalate', setElevationStatus(true));
    Actions.addMethod('trc_deescalate', setElevationStatus(false));
    Actions.addPostMethodToType('trc_escalate', 'workflowstatus', reloadRequirements);
    Actions.addPostMethodToType('trc_deescalate', 'workflowstatus', reloadRequirements);

    function setElevationStatus(setting){
        return function(regionObject, action){
            var escalationUrl;
            if (setting) {
                escalationUrl = regionObject.helpers.escalate_url;
            } else {
                escalationUrl = regionObject.helpers.deescalate_url;
            }
            return $http.patch(escalationUrl, {}).then(function(){
                lazyCallMethod('reload', regionObject);
                regionObject.controller.success();
                return regionObject;
            }, function(data){
                regionObject.controller.error(data.data);
            });
        }
    }

    function reloadRequirements(regionObject) {
        regionObject.$element.scope().statusCtrl.requirements.reload();
    }
});
