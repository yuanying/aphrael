'use strict';

const express = require('express');
const app = express();
const path = require('path');
const config = require('../../config');
const isProduction = process.env.NODE_ENV === 'production';

if(!isProduction) {
    const webpack = require('webpack');
    const webpackConfig = require('../../webpack.config.js');
    const compiler = webpack(webpackConfig);

    app.use(require('webpack-dev-middleware')(compiler, {
        noInfo: true, publicPath: webpackConfig.output.publicPath
    }));
    app.use(require('webpack-hot-middleware')(compiler));
}

app.use(express.static(config.distDir));
app.get('/', (req, res) => {
    res.sendFile(path.join(config.distDir, 'index.html'));
});

const server = app.listen(3000, () => {

  var port = server.address().port;
  console.log('Example app listening at http://%s:%s',
              server.address().address,
              server.address().port);
});
