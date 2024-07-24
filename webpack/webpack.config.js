const path = require('path');
const _ = require('lodash');

const webpack = require('webpack');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

const Visualizer = require('webpack-visualizer-plugin');

const joinPath = _.partial(path.join, __dirname);
const vendorStatic = ref => path.join('../axis/core/static/js/vendor', ref);
const appSrcTree = (app, ref) => path.join('../axis', app, 'webpack', ref);

module.exports = {
    mode: 'production',
    entry: {
        collection: appSrcTree('checklist', 'collection'),
        checklist: appSrcTree('checklist', 'checklist'),
        login: appSrcTree('core', 'login'),
        auth: appSrcTree('core', 'auth'),
        impersonate: appSrcTree('core', 'impersonate'),
        zendesk: appSrcTree('core', 'zendesk')
    },
    resolve: {
        modules: [
            path.resolve('entries'),
            path.resolve('node_modules'),
        ],
    },
    plugins: [
        new Visualizer()
    ],
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                parallel: true,
                uglifyOptions: {
                    mangle: false
                }
            })
        ],
        splitChunks: {
            chunks: 'all'
        }
    },
    output: {
        path: joinPath('dist'),
        filename: '[name].bundle.js'
    },
    externals: {
        angular: 'angular'
        // Not sure how to include ui-angular, @uirouter, lodash, jquery
    },
    module: {
        rules: [
            {
                test: /\.js$/, exclude: /node_modules/, use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            require.resolve('@babel/preset-env')
                        ]
                    }
                }
            }
        ]
    },
    performance: {
        hints: false,
        maxEntrypointSize: 512000,
        maxAssetSize: 512000
    }
};
