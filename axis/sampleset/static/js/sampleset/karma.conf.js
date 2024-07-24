// Karma configuration
// Generated on Tue Aug 26 2014 13:48:48 GMT-0700 (MST)

module.exports = function(config){
    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: '../),


        // frameworks to use
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['jasmine'],


        // list of files / patterns to load in the browser
        files: [
            '../../../../core/static/js/vendor/jquery/1.11.0/jquery-1.11.0.min.js',
            '../../../core/static/js/vendor/angular/1.2.21/angular.js',
            '../../../core/static/js/vendor/angular-mocks/1.2.25/angular-mocks.js',
            '../../../core/static/js/vendor/angular-route/1.2.25/angular-route.js',
            '../../../core/static/js/vendor/angular-ui-bootstrap/0.11.0/ui-bootstrap.js',
            '../../../core/static/js/vendor/angular-ui-bootstrap/0.11.0/ui-bootstrap-tpls.js',
            'tests/**/*.js',
            'SampleSetControlCenterApp.js',
            'tests/test_helpers.js',
            'controllers.js',
            'directives.js',
            'services.js',
            'filters.js',
            '../templates/*.html'
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
            'app.js': ['coverage'],
            'controllers.js': ['coverage'],
            'directives.js': ['coverage'],
            'services.js': ['coverage'],
            'filters.js': ['coverage'],
            '../templates/*.html': ['ng-html2js']
        },

        ngHtml2JsPreprocessor: {
            stripPrefix: '/(.*?)(?=/static|$)',
            moduleName: 'templates'
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
//            'Chrome'
        ],


        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false
    });
};
