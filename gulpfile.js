'use strict';
const gulp = require('gulp');
const gutil = require('gulp-util');
const eslint = require('gulp-eslint');
const config = require('./config');
const webpackConfig = require('./webpack.config');
const webpack = require('webpack');

gulp.task('webpack', (callback) => {
    let myConfig = Object.create(webpackConfig);
    webpack(myConfig, function(err, stats) {
        if(err) throw new gutil.PluginError('webpack', err);
        gutil.log('[webpack]', stats.toString({
            colors: true
        }));
        callback();
    });
});

gulp.task('lint', () => {
    return gulp.src(config.gulpServerSrc)
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failOnError());
});

gulp.task('watch', () => {
    gulp.watch('app/client/**/*', ['webpack']);
});

gulp.task('default', ['webpack']);
