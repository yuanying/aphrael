#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2009, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

'''
Simplified resource resolver that uses package-internal _resources directory.
'''

import builtins
import os
import sys

from calibre import config_dir

user_dir = os.path.join(config_dir, 'resources')


def _find_resources_dir():
    '''Find the resources directory, checking multiple locations.'''
    # 1. Check for sys.resources_location (calibre standard)
    if hasattr(sys, 'resources_location'):
        return sys.resources_location

    # 2. Check for _resources inside the calibre package
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pkg_resources = os.path.join(pkg_dir, '_resources')
    if os.path.isdir(pkg_resources):
        return pkg_resources

    # 3. Check for resources/ in the project root (development mode)
    # Go up from src/calibre/utils/ to project root
    project_root = os.path.dirname(os.path.dirname(pkg_dir))
    dev_resources = os.path.join(project_root, 'resources')
    if os.path.isdir(dev_resources):
        return dev_resources

    # 4. Check CALIBRE_DEVELOP_FROM
    dev_path = os.environ.get('CALIBRE_DEVELOP_FROM', None)
    if dev_path is not None:
        dev_path = os.path.join(os.path.abspath(os.path.dirname(dev_path)), 'resources')
        if os.path.isdir(dev_path):
            return dev_path

    # Fallback: use the package directory itself
    return pkg_dir


class PathResolver:

    def __init__(self):
        self.default_path = _find_resources_dir()
        self.locations = [self.default_path]
        self.cache = {}

        self.user_path = None
        if os.path.exists(user_dir) and os.path.isdir(user_dir):
            self.locations.insert(0, user_dir)
            self.user_path = user_dir

    def __call__(self, path, allow_user_override=True):
        path = path.replace(os.sep, '/')
        key = (path, allow_user_override)
        ans = self.cache.get(key, None)
        if ans is None:
            for base in self.locations:
                if not allow_user_override and base == self.user_path:
                    continue
                fpath = os.path.join(base, *path.split('/'))
                if os.path.exists(fpath):
                    ans = fpath
                    break

            if ans is None:
                ans = os.path.join(self.default_path, *path.split('/'))

            self.cache[key] = ans

        return ans

    def set_data(self, path, data=None):
        self.cache.pop((path, True), None)
        fpath = os.path.join(user_dir, *path.split('/'))
        if data is None:
            if os.path.exists(fpath):
                os.remove(fpath)
        else:
            base = os.path.dirname(fpath)
            if not os.path.exists(base):
                os.makedirs(base)
            with open(fpath, 'wb') as f:
                f.write(data)


_resolver = PathResolver()


def get_path(path, data=False, allow_user_override=True):
    fpath = _resolver(path, allow_user_override=allow_user_override)
    if data:
        with open(fpath, 'rb') as f:
            return f.read()
    return fpath


def get_image_path(path, data=False, allow_user_override=True):
    if not path:
        return get_path('images', allow_user_override=allow_user_override)
    return get_path('images/'+path, data=data, allow_user_override=allow_user_override)


def set_data(path, data=None):
    return _resolver.set_data(path, data)


def get_user_path():
    return _resolver.user_path


builtins.__dict__['P'] = get_path
builtins.__dict__['I'] = get_image_path
