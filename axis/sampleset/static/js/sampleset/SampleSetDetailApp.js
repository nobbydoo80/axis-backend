/**
 * Created by mjeffrey on 10/24/14.
 */
var app = angular.module('SampleSetDetailApp', [
    'ui.bootstrap',
    'axis.controllers',
    'axis.services',
    'axis.directives',
    'axis.filters'
]);
app.config(function($interpolateProvider, $httpProvider, $sceDelegateProvider, ExamineSettings){
    $sceDelegateProvider.resourceUrlWhitelist([
        'self',
        ExamineSettings.static_url + '**'
    ]);

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});
app.constant('CustomEvents', {
    OPEN_ACCORDION: 'openAccordion',
    suffixes: {
        UPDATE_ANSWERS: ':answersUpdated',
        HOME_MOVE: ':homeMoved'
    }
});
app.controller('SampleSetDetailController', function($scope, SampleSetProperties){
    $scope.viewingSampleSets = SampleSetProperties.getObject().viewingSampleSets;

    $scope.go = function(id){
        SampleSetProperties.addSampleSet(id);
    }
});
