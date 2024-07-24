/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.actionStrip.actionStripSet')
.controller('ActionStripSetController', function(){
    var ctrl = this;

    ctrl.singleInstance = false;
    ctrl.actionsAttribute = false;
})
.directive('standaloneActionStripSet', function(){
    return {
        restrict: 'EA',
        scope: true,
        templateUrl: '/examine/actions/action-strip.html',
        controller: 'ActionStripSetController',
        controllerAs: 'stripSet',
        link: function(scope, element, attrs){
            var listener = scope.$watch(attrs.actions, function(newVal, oldVal){
               scope.actionsObject = newVal;
            });

            scope.$on('$destroy', function(){
                listener();
            });
        }
    }
})
.directive('actionStripSet', function(){
    /**
     * Used when you need to place controls somewhere on the page.
     *
     * Default use is with the 'actions' attr.
     *    Pass it the regionObjects .actions dict.
     *
     * For single instances use the single-instance attr.
     *    Pass it the string of the action for it to look up in regionObject.actions
     */
    return {
        restrict: 'EA',
        require: '^?axisRegion',
        scope: true,
        templateUrl: '/examine/actions/action-strip.html',
        controller: 'ActionStripSetController',
        controllerAs: 'stripSet',
        link: function(scope, element, attrs, regionController){
            if(regionController){
                var actionAttr = attrs.actions || 'regionObject.actions';

                scope.singleInstance = attrs.singleInstance;
                scope.actionsObject = scope.$eval(actionAttr);
            }
        }
    }
});
