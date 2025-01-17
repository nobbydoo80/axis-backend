var webpack = require('webpack'),
    path    = require('path'),
    _       = require('lodash'),
    aliases = require('./webpack.aliases.js'),
    vendor  = require('./webpack.vendor.config.js');

var joinPath = _.partial(path.join, __dirname);

module.exports = {
    entry: {
        vendor: vendor.vendor,
        helpers: vendor.helpers,
        examine: vendor.examine,
        app: './app.js',
    },
    output: {
        path: joinPath('/build/'),
        filename: '[name].bundle.js',
        jsonpFunction: 'webpackJsonpLegacy',
        // publicPath: '/static/js/build/'  # This is declared in global_base.html
    },
    //externals: {
    //    'jquery': '$',
    //    'angular': 'angular',
    //    'lodash': '_'
    //},
    resolve: {
        root: [joinPath('node_modules')],
        alias: aliases
    },
    resolveLoader: {
        root: [joinPath('node_modules')],
    },
    module: {
        loaders: [
            {test: /\.js$/, exclude: /(node_modules|vendor)(?!.*wrapper)/, loader: 'babel-loader'},
            {test: require.resolve('lodash'), loader: 'expose?_', exclude: /node_modules/},
            {test: /ui-bootstrap/, loader: 'imports?angular', exclude: /node_modules/},
            {test: /vendor.*dataTable/, loader: 'imports?exports=>false', exclude: /node_modules/}
        ],
        noParse: [/vendor(?!.*(wrapper|jquery.dataTables|dataTables.bootstrap|ui-bootstrap))/]
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin('vendor', 'vendor.bundle.js'),
        new webpack.optimize.OccurrenceOrderPlugin()
        //new webpack.optimize.UglifyJsPlugin({mangle: false, compress: {unused: false, dead_code: false, warnings: false}, test: /vendor|helpers|lazy/})
    ]

};
