/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.region.regionSet', ['axis.region.region', 'axis.services.RegionService', 'axis.services.HttpQueue']);
angular.module('axis.region.regionSetSideTabs', ['axis.region.regionSet']);
angular.module('axis.region.singleRegion', ['axis.region.region', 'axis.services.RegionService', 'axis.services.UrlService', 'axis.services.Actions', 'axis.services.HttpQueue']);
angular.module('axis.region.region', ['axis.services.Actions']);
angular.module('axis.region.helpers', []);

angular.module('axis.region', [
    'axis.region.regionSet',
    'axis.region.regionSetSideTabs',
    'axis.region.singleRegion',
    'axis.region.region',
    'axis.region.helpers'
]);
