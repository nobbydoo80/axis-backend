/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.actionStrip.actionStrip')
.controller('ActionStripController', function(){
    // empty controller so directives can require this.
})
.directive('actionStrip', function(){
    return {
        restrict: 'EA',
        require: '^actionStripSet',
        controller: 'ActionStripController'
    }
});
