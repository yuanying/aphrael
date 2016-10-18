'use strict';
const path = require('path');

const rootDir = '/usr/src/app';
const appDir = path.join(rootDir, 'app');
const distDir = path.join(rootDir, 'dist');
const serverDir = path.join(appDir, 'server');

const config = {
    distDir: distDir,
    gulpServerSrc: serverDir+'/*.js'
};

module.exports = config;
