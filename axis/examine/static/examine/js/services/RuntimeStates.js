/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.services.RuntimeStates')
.provider('RuntimeStates', function($stateProvider){
    this.$get = function(){
        return {
            addState: function(name, state){
                $stateProvider.state(name, state);
            }
        }
    }
});
