/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.actionStrip.actionStrip')
.directive('actionButton', function(){
    /**
     * Action buttons can be made manually by passing in attributes.
     * The exception is dropdown buttons. Those required a nice options object.
     */
    return {
        restrict: 'EA',
        require: '^actionStrip',
        scope: {
            type: '@?btnType',
            style: '@?btnStyle',
            size: '@?btnSize',
            instruction: '@?',
            href: '@?link',
            disabled: '=?',

            options: '=?'
        },
        transclude: true,
        templateUrl: '/examine/actions/angular-button.html',
        link: function(scope, element, attrs){
            scope.region = scope.$parent.region;
            scope.getType = function(){
                return scope.type || scope.options.type;
            }
        }
    }
});
