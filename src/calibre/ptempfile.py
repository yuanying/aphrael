__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'
'''
Provides platform independent temporary files that persist even after
being closed.
'''
import os
import tempfile
from contextlib import contextmanager

from calibre.constants import __appname__, filesystem_encoding
from calibre.utils.safe_atexit import remove_dir, remove_file_atexit, remove_folder_atexit, unlink

_base_dir = None
_prevent_recursion = False
cleanup = unlink


get_default_tempdir = tempfile.gettempdir


def base_dir():
    global _base_dir, _prevent_recursion
    if _base_dir is not None and not os.path.exists(_base_dir):
        if _prevent_recursion:
            _base_dir = get_default_tempdir()
        else:
            _base_dir = None
    if _base_dir is None:
        td = os.environ.get('CALIBRE_WORKER_TEMP_DIR', None)
        if td is not None:
            from calibre.utils.serialize import msgpack_loads
            from polyglot.binary import from_hex_bytes
            try:
                td = msgpack_loads(from_hex_bytes(td))
            except Exception:
                td = None
        if td and os.path.exists(td):
            _base_dir = td
        else:
            base = os.environ.get('CALIBRE_TEMP_DIR', None)
            prefix = f'{__appname__}-'
            _base_dir = tempfile.mkdtemp(prefix=prefix, dir=base or get_default_tempdir())
            orig = _prevent_recursion
            _prevent_recursion = True
            try:
                remove_folder_atexit(_base_dir)
            finally:
                _prevent_recursion = orig

    return _base_dir


def fix_tempfile_module():
    global get_default_tempdir
    if tempfile._gettempdir is not base_dir:
        get_default_tempdir = tempfile._gettempdir
        tempfile._gettempdir = base_dir


def reset_base_dir():
    global _base_dir
    _base_dir = None


@contextmanager
def override_base_dir(newval: str) -> None:
    global _base_dir
    before, _base_dir = _base_dir, newval
    try:
        yield
    finally:
        _base_dir = before


def force_unicode(x):
    if isinstance(x, bytes):
        x = x.decode(filesystem_encoding)
    return x


def _make_file(suffix, prefix, base):
    suffix, prefix = map(force_unicode, (suffix, prefix))  # no2to3
    return tempfile.mkstemp(suffix, prefix, dir=base)


def _make_dir(suffix, prefix, base):
    suffix, prefix = map(force_unicode, (suffix, prefix))  # no2to3
    return tempfile.mkdtemp(suffix, prefix, base)


class PersistentTemporaryFile:
    '''
    A file-like object that is a temporary file that is available even after being closed on
    all platforms. It is automatically deleted on normal program termination.
    '''
    _file = None

    def __init__(self, suffix='', prefix='', dir=None, mode='w+b'):
        if prefix is None:
            prefix = ''
        if dir is None:
            dir = base_dir()
        fd, name = _make_file(suffix, prefix, dir)

        self._file = os.fdopen(fd, mode)
        self._name = name
        self._fd = fd
        remove_file_atexit(name)

    def __getattr__(self, name):
        if name == 'name':
            return self.__dict__['_name']
        return getattr(self.__dict__['_file'], name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def PersistentTemporaryDirectory(suffix='', prefix='', dir=None):
    '''
    Return the path to a newly created temporary directory that will
    be automatically deleted on application exit.
    '''
    if dir is None:
        dir = base_dir()
    tdir = _make_dir(suffix, prefix, dir)
    remove_folder_atexit(tdir)
    return tdir


class TemporaryDirectory:
    '''
    A temporary directory to be used in a with statement.
    '''

    def __init__(self, suffix='', prefix='', dir=None, keep=False):
        self.suffix = suffix
        self.prefix = prefix
        if dir is None:
            dir = base_dir()
        self.dir = dir
        self.keep = keep

    def __enter__(self):
        if not hasattr(self, 'tdir'):
            self.tdir = _make_dir(self.suffix, self.prefix, self.dir)
        return self.tdir

    def __exit__(self, *args):
        if not self.keep and os.path.exists(self.tdir):
            remove_dir(self.tdir)


class TemporaryFile:

    def __init__(self, suffix='', prefix='', dir=None, mode='w+b'):
        if prefix is None:
            prefix = ''
        if suffix is None:
            suffix = ''
        if dir is None:
            dir = base_dir()
        self.prefix, self.suffix, self.dir, self.mode = prefix, suffix, dir, mode
        self._file = None

    def __enter__(self):
        fd, name = _make_file(self.suffix, self.prefix, self.dir)
        self._file = os.fdopen(fd, self.mode)
        self._name = name
        self._file.close()
        return name

    def __exit__(self, *args):
        unlink(self._name)


class SpooledTemporaryFile(tempfile.SpooledTemporaryFile):

    def __init__(self, max_size=0, suffix='', prefix='', dir=None, mode='w+b',
            bufsize=-1):
        if prefix is None:
            prefix = ''
        if suffix is None:
            suffix = ''
        if dir is None:
            dir = base_dir()
        self._name = None
        tempfile.SpooledTemporaryFile.__init__(self, max_size=max_size,
                suffix=suffix, prefix=prefix, dir=dir, mode=mode)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    def readable(self):
        return self._file.readable()

    def seekable(self):
        return self._file.seekable()

    def writable(self):
        return self._file.writable()


def better_mktemp(*args, **kwargs):
    fd, path = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    return path
