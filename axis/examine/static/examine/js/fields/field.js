/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.fields.field')
.directive('axisField', function($timeout){
    /**
     * Attributes:
     *  field: ={field object}
     *  on-change: &
     *  show-label: {no arguments}
     *  label: @
     *  disabled: =
     */
    return {
        restrict: 'EA',
        require: '^?ngRepeat',
        scope: true,
        templateUrl: '/examine/angular_field.html',
        controller: function($scope){
            $scope.hasAttr = hasAttr;

            function hasAttr(attr){
                return $scope.field.widget.attrs.hasOwnProperty(attr);
            }
        },
        link: function(scope, element, attrs){

            if(!angular.isDefined(scope.field)){
                set_field();
                if(!angular.isDefined(scope.field)) {
                    throw new Error("Axis Field requires 'field'.");
                }
                scope.regionObject.controller.axisFields[scope.field.field_name] = element;
            }
            var initial_value = (attrs.value ? scope.$eval(attrs.value) : scope.field.value);
            if (attrs.value || (initial_value !== null && initial_value !== undefined && initial_value !== "")) {
                scope.regionObject.object[scope.field.field_name] = initial_value;
            }

            // NOTE: implementation taken from ngChange
            scope.onChange = function(data){
                if(angular.isDefined(attrs.onChange)){
                    scope.$eval(attrs.onChange, data);
                }
            };

            // Options for overwriting labels
            scope.showLabel = !angular.isDefined(attrs.noLabel);
            if(angular.isDefined(attrs.label)){
                scope.label = scope.$eval(attrs.label);
            }

            // Options for forcefully disabling fields
            if(angular.isDefined(attrs.disabled)){
                scope.field.widget.attrs.disabled = scope.$eval(attrs.disabled);
            }

            function set_field(){
                scope.field = scope.$eval(attrs.field);
                if(angular.isDefined(attrs.expectUpdate)){
                    scope.$watch(attrs.field, function(value){
                        scope.field = value;
                    });
                }
            }
        }
    }
})
.directive('fieldError', function(){
    /**
     * Place this anywhere there is access to the `regionObject` and `field` and it will
     * display any non_field_errors returned by the server.
     */
    return {
        restrict: 'EA',
        replace: true,
        template: '<ul class="text-danger" ng-if="regionObject.errors[field.field_name]">\n    <li ng-repeat="message in regionObject.errors[field.field_name] track by $index">[[ message ]]</li>\n</ul>'
    }
});
