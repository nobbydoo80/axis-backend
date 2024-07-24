const baseConfig = require('./webpack.config.js');

module.exports = Object.assign({}, baseConfig, {
  mode: 'development',
  plugins: [
  ],
  optimization: {
    splitChunks: {
      chunks: 'all'
    }
  }
});
