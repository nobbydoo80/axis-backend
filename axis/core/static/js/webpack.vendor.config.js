var webpack = require('webpack');
var path = require('path');
var _ = require('lodash');
var aliases = require('./webpack.aliases.js');

var joinPath = _.partial(path.join, __dirname);

module.exports = {
    vendor: [
        // settings the public path
        'core/publicPath.js',

        // jquery
        // needed because of jquery@1 export badness.
        joinPath('./vendor/jquery/jquery_wrapper'),
        joinPath('./plugins/jquery/jquery.dndPageScroll.js'),
        joinPath('./plugins/jquery/jquery.formset.js'),
        joinPath('./plugins/jquery/jquery.multi-select.js'),
        joinPath('./plugins/jquery/jquery.quicksearch.js'),
        joinPath('./plugins/jquery/jquery.validate.js'),

        // datatables
        'datatables',
        joinPath('./plugins/datatable/jquery.dataTables.fnReloadAjax.js'),
        joinPath('./plugins/datatable/jquery.dataTables.fnSortNeutral.js'),
        joinPath('./vendor/datatable/1.10.9/buttons/1.0.3/dataTables.buttons.js'),
        joinPath('./vendor/datatable/1.10.9/buttons/1.0.3/buttons.bootstrap.js'),
        joinPath('./vendor/datatable/1.10.9/buttons/1.0.3/buttons.html5.js'),
        joinPath('./vendor/datatable/1.10.9/buttons/1.0.3/buttons.print.js'),


        // extras
        'angular',
        'ng-duallist',
        'ui-bootstrap',
        'bootstrap',
        'lodash',
        'expose?moment!moment'
    ],
    helpers: [
        joinPath('./vendor/datatable/1.10.9/dataTables.bootstrap.js'),
        joinPath('./vendor/pdfmake/pdfmake_wrapper'),
        joinPath('./vendor/jszip/jszip_wrapper'),
        joinPath('./helpers/datatable/jquery.dataTables.defaults.js'),
        joinPath('./helpers/handlebars/handlebars_helpers.js'),
        joinPath('./helpers/select2/dynamic_add.js')
    ],
    examine: [
            'examine/action_strip/index.js',
            'examine/action_strip/actionButton.js',
            'examine/action_strip/actionStrip.js',
            'examine/action_strip/actionStripSet.js',
            'examine/fields/index.js',
            'examine/fields/field.js',
            'examine/fields/helpers.js',
            'examine/region/index.js',
            'examine/region/regionSet.js',
            'examine/region/singleRegion.js',
            'examine/region/region.js',
            'examine/region/helpers.js',
            'examine/services/index.js',
            'examine/services/Actions.js',
            'examine/services/Modal.js',
            'examine/services/HttpQueue.js',
            'examine/services/RegionService.js',
            'examine/services/RuntimeStates.js',
            'examine/services/TabService.js',
            'examine/services/UrlService.js',
            'examine/filters.js',
            'examine/app.js',
            joinPath('./vendor/angular-ui-select/0.19.8/select.min.js'),
            joinPath('./vendor/angular-ui-bootstrap/0.12.0/ui-bootstrap-tpls.js'),
            joinPath('./vendor/angular-ui-router/0.2.11/angular-ui-router.js'),
            joinPath('./vendor/angular-multi-select/angular-multi-select.js'),
            'angular-moment',
            'moment-duration-format'
    ]
};
