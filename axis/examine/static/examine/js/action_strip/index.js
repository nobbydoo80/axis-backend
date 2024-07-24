/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.actionStrip.actionStripSet', ['axis.actionStrip.actionStrip', 'axis.actionStrip.actionButton']);
angular.module('axis.actionStrip.actionStrip', []);
angular.module('axis.actionStrip.actionButton', []);

angular.module('axis.actionStrip', [
    'axis.actionStrip.actionStripSet',
    'axis.actionStrip.actionStrip',
    'axis.actionStrip.actionButton'
]);
