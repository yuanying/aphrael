'use strict';
const gulp = require('gulp');
const gutil = require('gulp-util');
const eslint = require('gulp-eslint');
const nodemon = require('gulp-nodemon');
const config = require('./config');
const webpackConfig = require('./webpack.config');
const webpack = require('webpack');

gulp.task('nodemon', () => {
  nodemon({
      script: './app/server/server.js',
      ext: 'js',
      watch: ['./app/server'],
      env: { 'NODE_ENV': 'development' }
  })
});

gulp.task('copy-to-example', ['webpack'], () => {
  return gulp.src(
    [ 'dist/*.html', 'dist/js/**', 'dist/images/**' ],
    { base: 'dist' }
  )
  .pipe( gulp.dest( 'example' ) );
});

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
    gulp.watch('app/client/**/*', ['copy-to-example']);
});

gulp.task('default', ['copy-to-example']);
