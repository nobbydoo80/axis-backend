/**
 * Created by mjeffrey on 10/20/14.
 */

var dependencies = [
    'ui.bootstrap',
    'ui.router',
    'ui.select',
    'axis.filters',
    'axis.services',
    'axis.fields',
    'axis.region',
    'axis.actionStrip',
];

function getDependencies(deps){
    var temp = angular.copy(dependencies);
    if(typeof deps !== 'undefined'){
        angular.forEach(deps, function(dep){
            temp.push(dep);
        })
    }
    return temp;
}

angular.module('examineApp', getDependencies(window.__extraDependencies))
.controller('ExamineViewController', function($rootScope, $state, $scope, ExamineSettings, TabService, RegionService){
    var ctrl = this;

    $rootScope.ExamineSettings = ExamineSettings;
    $rootScope.isHiddenField = isHiddenField;
    $rootScope.$state = $state;
    $rootScope.creating = ctrl.creating = ExamineSettings.creating;
    ctrl.pageRegions = $scope.pageRegions = ExamineSettings.regions_endpoints;
    ctrl.tabsActive = $scope.tabsActive = TabService.tabs;
    ctrl.regionsMap = RegionService.helpers.regionsMap;
    ctrl.getRegionCounter = RegionService.getRegionCounter;
    $rootScope.examineApp = ctrl;

    function isHiddenField(field){
        if(field.widget.input_type == 'hidden'){
            if(field.widget._widget.toLowerCase().indexOf('hidden') > -1){
                return true;
            }
        }
        return false;
    }
})
.constant('ExamineSettings', window.__ExamineSettings)
.config(function($httpProvider, $interpolateProvider, $sceDelegateProvider, ExamineSettings, $stateProvider, uiSelectConfig, $provide){

    $sceDelegateProvider.resourceUrlWhitelist([
            'self',
            ExamineSettings.static_url + '**'
    ]);

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    uiSelectConfig.theme = 'select2';

    $stateProvider.state('index', {url: '/'});
});
