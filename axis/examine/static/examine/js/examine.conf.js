// Karma configuration
// Generated on Mon Oct 20 2014 12:51:23 GMT-0700 (MST)

module.exports = function(config){
    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: '',


        // frameworks to useO
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['jasmine'],


        // list of files / patterns to load in the browser
        files: [
            '../../../../core/static/js/vendor/jquery/1.11.0/jquery-1.11.0.min.js',
            '../../../../core/static/js/vendor/angular/1.3.6/angular.min.js',
            '../../../../core/static/js/vendor/angular-mocks/1.3.6/angular-mocks.min.js',
            '../../../../core/static/js/vendor/angular-ui-router/0.2.11/angular-ui-router.min.js',
            '../../../../core/static/js/vendor/angular-multi-select/angular-multi-select.min.js',
            '../../../../core/static/js/vendor/angular-ui-select/0.7.0/ui-select.min.js',
            '../../../../core/static/js/vendor/angular-ui-bootstrap/0.11.0/ui-bootstrap-tpls.min.js',
            '../../../../core/static/js/angular-google-maps/lodash.min.js',
            './tests/test_helpers.js',
            // need to make sure the index.js files are loaded first.
            // APP
            './app.js',
            // ACTION STRIP
            './action_strip/index.js',
            './action_strip/actionStrip.js',
            './action_strip/actionStripSet.js',
            './action_strip/actionButton.js',

            // REGION
            './region/index.js',
            './region/region.js',
            './region/singleRegion.js',
            './region/regionSet.js',

            // FIELDS
            './fields/index.js',
            './fields/field.js',

            // SERVICES
            './services/index.js',
            './services/Actions.js',
            './services/RegionService.js',
            './services/HttpQueue.js',
            './services/Modal.js',
            './services/UrlService.js',
            './services/TabService.js',
            './services/RuntimeStates.js',

            // FILTERS
            './filters.js',
            //'./region/index.js',
            //'./services/index.js',
            //'./fields/index.js',
            //'./action_strip/index.js',
            //'./action_strip/.*[^index].js',
            //'./region/*.js',
            //'./services/*.js',
            //'./fields/*.js',
            //'./*.js',
            '../../../templates/examine/**/*.html',
            './tests/**/*.js'
        ],

        plugins: [
            'karma-phantomjs-launcher',
            'karma-jasmine',
            'karma-coverage',
            'karma-ng-html2js-preprocessor'
        ],


        // list of files to exclude
        exclude: [
        ],


        // preprocess matching files before serving them to the browser
        // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {
            '*.js': ['coverage'],
            './action_strip/*.js': ['coverage'],
            './region/*.js': ['coverage'],
            './services/*.js': ['coverage'],
            './services/actions/*.js': ['coverage'],
            '../../../templates/examine/actions/*.html': ['ng-html2js'],
            '../../../templates/examine/*.html': ['ng-html2js']
        },

        ngHtml2JsPreprocessor: {
            // TODO: better regex to capture second /examine/
            stripPrefix: '/(.*?)(?=/examine/actions|/examine/angular|$)',
            moduleName: 'templates'
        },

        proxies: {
            '/api/v2/': 'http://127.0.0.1:8000/api/v2/'
        },


        // test results reporter to use
        // possible values: 'dots', 'progress'
        // available reporters: https://npmjs.org/browse/keyword/karma-reporter
        reporters: ['progress', 'coverage'],


        // web server port
        port: 9876,


        // enable / disable colors in the output (reporters and logs)
        colors: true,


        // level of logging
        // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
        logLevel: config.LOG_INFO,


        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,


        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        browsers: [
            'PhantomJS'
            //'Chrome'
        ],


        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false
    });
};
