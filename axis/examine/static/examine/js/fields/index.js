/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.fields.field', []);
angular.module('axis.fields.helpers', ['axis.fields.field', 'axis.fields.helpers.tab', 'axis.fields.helpers.fileField', 'axis.fields.helpers.select2', 'axis.fields.helpers.multiSelect', 'axis.fields.helpers.datepicker']);

angular.module('axis.fields.helpers.tab', ['axis.services.TabService', 'ui.bootstrap']);
angular.module('axis.fields.helpers.fileField', []);
angular.module('axis.fields.helpers.select', []);
angular.module('axis.fields.helpers.select2', ['ui.select']);
angular.module('axis.fields.helpers.multiSelect', ['multi-select']);
angular.module('axis.fields.helpers.datepicker', ['ui.bootstrap.datepicker']);


angular.module('axis.fields', [
    'axis.fields.field',
    'axis.fields.helpers'
]);
