/**
 * Created by mjeffrey on 9/8/14.
 */
var f = angular.module('axis.filters', []);

f.filter('split', function(){
    return function(input, splitChar, splitIndex){
        if(typeof input == 'string') return input.split(splitChar)[splitIndex] || '';
    }
});
