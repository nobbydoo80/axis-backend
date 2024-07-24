/**
 * Created by mjeffrey on 11/5/14.
 */

// ACTIONS
angular.module('axis.services.Actions', [
    'axis.services.RegionService',
    'axis.services.Modal',
    'axis.services.HttpQueue'
]);

// OTHER
angular.module('axis.services.Modal', ['ui.bootstrap']);
angular.module('axis.services.HttpQueue', []);
angular.module('axis.services.RuntimeStates', ['ui.router']);
angular.module('axis.services.TabService', ['axis.services.RuntimeStates', 'ui.router']);
angular.module('axis.services.RegionService', []);
angular.module('axis.services.UrlService', ['ui.router']);

angular.module('axis.services', [
    'axis.services.Actions',
    'axis.services.Modal',
    'axis.services.HttpQueue',
    'axis.services.RuntimeStates',
    'axis.services.TabService',
    'axis.services.RegionService',
    'axis.services.UrlService'
]);
