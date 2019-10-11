'use strict';
const webpack = require('webpack');
const path = require('path');
module.exports = {
    entry: [
        path.join(__dirname, 'app/client/js/main.js')
    ],
    output: {
        path: path.join(__dirname, 'dist/js'),
        filename: '[name].js',
        publicPath: '/js/'
    },
    mode: 'production',
    module: {
        rules: [{
            test: /\.js?$/,
            enforce: "pre",
            exclude: /node_modules/,
            use: [{
                loader: "eslint-loader"
            }]
        }, {
            test: /\.js?$/,
            exclude: /node_modules/,
            use:[{
                loader: 'babel-loader',
                options: {
                    presets: ["@babel/preset-env"]
                }
            }]
        }, {
            test: /bootstrap\/js\//,
            use:[{
                loader: 'imports-loader',
                options:{
                    jQuery: 'jquery'
                }
            }]
        }, {
            test   : /\.css$/,
            use: [
                "style-loader",
                "css-loader"
            ]
        }, {
            test: /\.(png|woff|woff2|eot|ttf|svg|gif)$/,
            use: [{
                loader: "url-loader",
                options: {
                    limit: "100000"
                }
            }]
        }]
    }
};
