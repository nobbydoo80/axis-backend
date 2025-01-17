/**
 * Created by mjeffrey on 8/26/14.
 */
var app = angular.module('SampleSetControlCenterApp', [
    'ui.bootstrap',
    'axis.controllers',
    'axis.services',
    'axis.directives',
    'axis.filters',
    'ngRoute'
]);

app.config(function($interpolateProvider, $httpProvider, $routeProvider, $sceDelegateProvider, ExamineSettings){

    $sceDelegateProvider.resourceUrlWhitelist([
        'self',
        ExamineSettings.static_url + '**'
    ]);

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    $routeProvider
    .when('/', {
        templateUrl: ExamineSettings.static_url + 'templates/index.html',
        controller: 'AppController',
        reloadOnSearch: false
    })
    .otherwise({redirectTo: '/'})
});

app.constant('CustomEvents', {
    OPEN_ACCORDION: 'openAccordion',
    suffixes: {
        UPDATE_ANSWERS: ':answersUpdated',
        HOME_MOVE: ':homeMoved'
    }
});

$(function(){
    var appElement = $("[data-angular-app]");
    angular.bootstrap(appElement, [appElement.attr('data-angular-app')]);
});
