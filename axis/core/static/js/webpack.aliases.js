var path = require('path');
var _ = require('lodash');

var joinPath = _.partial(path.join, __dirname);

module.exports = {
    'core': joinPath('./core'),
    'examine': joinPath('./../../../examine/static/examine/js'),
    'checklist': joinPath('./../../../checklist/static/checklist/js'),
    'datatables': joinPath('./vendor/datatable/1.10.9/jquery.dataTables.js'),
    'ng-duallist': joinPath('./vendor/ng-duallist/ngduallist.js'),

    'bootstrap': joinPath('./vendor/bootstrap/3.3.2/bootstrap.js'),
    'ui-router': joinPath('./vendor/angular-ui-router/0.2.11/angular-ui-router.js'),
    'angular-ui-router': joinPath('./vendor/angular-ui-router/0.2.11/angular-ui-router.js'),
    'ui-bootstrap': joinPath('./vendor/angular-ui-bootstrap/0.12.0/ui-bootstrap-tpls.js'),
    'ui-router': joinPath('./vendor/angular-ui-router/0.2.11/angular-ui-router.js'),
    'angular-ui-router': joinPath('./vendor/angular-ui-router/0.2.11/angular-ui-router.js'),
    'multi-select': joinPath('./vendor/angular-multi-select/angular-multi-select.js')
};
