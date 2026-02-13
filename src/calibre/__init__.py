''' E-book management software'''
__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import os
import re
import sys
import time
import warnings
from functools import lru_cache, partial
from math import floor

from polyglot.builtins import hasenv

if not hasenv('CALIBRE_SHOW_DEPRECATION_WARNINGS'):
    warnings.simplefilter('ignore', DeprecationWarning)
try:
    os.getcwd()
except OSError:
    os.chdir(os.path.expanduser('~'))

from calibre.constants import (
    __appname__,
    __author__,
    __version__,
    config_dir,
    filesystem_encoding,
    is_debugging,
    isbsd,
    isfrozen,
    islinux,
    ismacos,
    plugins,
    preferred_encoding,
)
from calibre.constants import iswindows as iswindows
from calibre.startup import initialize_calibre

initialize_calibre()
from calibre.prints import prints as prints
from calibre.utils.icu import safe_chr
from calibre.utils.resources import get_path as P

if False:
    # Prevent pyflakes from complaining
    __appname__, islinux, __version__
    isfrozen, __author__, isbsd, config_dir, plugins

_mt_inited = False


def _init_mimetypes():
    global _mt_inited
    import mimetypes
    mimetypes.init([P('mime.types')])
    _mt_inited = True


@lru_cache(4096)
def guess_type(*args, **kwargs):
    import mimetypes
    if not _mt_inited:
        _init_mimetypes()
    return mimetypes.guess_type(*args, **kwargs)


def guess_all_extensions(*args, **kwargs):
    import mimetypes
    if not _mt_inited:
        _init_mimetypes()
    return mimetypes.guess_all_extensions(*args, **kwargs)


def guess_extension(*args, **kwargs):
    import mimetypes
    if not _mt_inited:
        _init_mimetypes()
    ext = mimetypes.guess_extension(*args, **kwargs)
    if not ext and args and args[0] == 'application/x-palmreader':
        ext = '.pdb'
    return ext


def get_types_map():
    import mimetypes
    if not _mt_inited:
        _init_mimetypes()
    return mimetypes.types_map


def to_unicode(raw, encoding='utf-8', errors='strict'):
    if isinstance(raw, str):
        return raw
    return raw.decode(encoding, errors)


def patheq(p1, p2):
    p = os.path

    def d(x):
        return p.normcase(p.normpath(p.realpath(p.normpath(x))))
    if not p1 or not p2:
        return False
    return d(p1) == d(p2)


def unicode_path(path, abs=False):
    if isinstance(path, bytes):
        path = path.decode(filesystem_encoding)
    if abs:
        path = os.path.abspath(path)
    return path


def osx_version():
    if ismacos:
        import platform
        src = platform.mac_ver()[0]
        m = re.match(r'(\d+)\.(\d+)\.(\d+)', src)
        if m:
            return int(m.group(1)), int(m.group(2)), int(m.group(3))


def confirm_config_name(name):
    return name + '_again'


_filename_sanitize_unicode = frozenset(('\\', '|', '?', '*', '<',        # no2to3
    '"', ':', '>', '+', '/') + tuple(map(chr, range(32))))  # no2to3


def sanitize_file_name(name, substitute='_'):
    '''
    Sanitize the filename `name`. All invalid characters are replaced by `substitute`.
    The set of invalid characters is the union of the invalid characters in Windows,
    macOS and Linux. Also removes leading and trailing whitespace.
    **WARNING:** This function also replaces path separators, so only pass file names
    and not full paths to it.
    '''
    if isbytestring(name):
        name = name.decode(filesystem_encoding, 'replace')
    if isbytestring(substitute):
        substitute = substitute.decode(filesystem_encoding, 'replace')
    chars = (substitute if c in _filename_sanitize_unicode else c for c in name)
    one = ''.join(chars)
    one = re.sub(r'\s', ' ', one).strip()
    bname, ext = os.path.splitext(one)
    one = re.sub(r'^\.+$', '_', bname)
    one = one.replace('..', substitute)
    one += ext
    # Windows doesn't like path components that end with a period or space
    if one and one[-1] in ('.', ' '):
        one = one[:-1]+'_'
    # Names starting with a period are hidden on Unix
    if one.startswith('.'):
        one = '_' + one[1:]
    return one


sanitize_file_name2 = sanitize_file_name_unicode = sanitize_file_name


class CommandLineError(Exception):
    pass


def setup_cli_handlers(logger, level):
    import logging
    if hasenv('CALIBRE_WORKER') and logger.handlers:
        return
    logger.setLevel(level)
    if level == logging.WARNING:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        handler.setLevel(logging.WARNING)
    elif level == logging.INFO:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter())
        handler.setLevel(logging.INFO)
    elif level == logging.DEBUG:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(filename)s:%(lineno)s: %(message)s'))

    logger.addHandler(handler)


def load_library(name, cdll):
    return cdll.LoadLibrary(name+'.so')


def extract(path, dir):
    extractor = None
    with open(path, 'rb') as f:
        id_ = f.read(3)
    if id_.startswith(b'PK'):
        from calibre.libunzip import extract as zipextract
        extractor = zipextract
    if extractor is None:
        ext = os.path.splitext(path)[1][1:].lower()
        if ext in ('zip', 'cbz', 'epub', 'oebzip'):
            from calibre.libunzip import extract as zipextract
            extractor = zipextract
    if extractor is None:
        raise Exception('Unknown archive type')
    extractor(path, dir)


def fit_image(width, height, pwidth, pheight):
    '''
    Fit image in box of width pwidth and height pheight.
    @param width: Width of image
    @param height: Height of image
    @param pwidth: Width of box
    @param pheight: Height of box
    @return: scaled, new_width, new_height. scaled is True iff new_width and/or new_height is different from width or height.
    '''
    if height < 1 or width < 1:
        return False, int(width), int(height)
    scaled = height > pheight or width > pwidth
    if height > pheight:
        corrf = pheight / float(height)
        width, height = floor(corrf*width), pheight
    if width > pwidth:
        corrf = pwidth / float(width)
        width, height = pwidth, floor(corrf*height)
    if height > pheight:
        corrf = pheight / float(height)
        width, height = floor(corrf*width), pheight

    return scaled, int(width), int(height)


class CurrentDir:

    def __init__(self, path):
        self.path = path
        self.cwd = None

    def __enter__(self, *args):
        self.cwd = os.getcwd()
        os.chdir(self.path)
        return self.cwd

    def __exit__(self, *args):
        try:
            os.chdir(self.cwd)
        except OSError:
            # The previous CWD no longer exists
            pass


_ncpus = None


def detect_ncpus():
    global _ncpus
    if _ncpus is None:
        _ncpus = max(1, os.cpu_count() or 1)
    return _ncpus


relpath = os.path.relpath


def walk(dir):
    ''' A nice interface to os.walk '''
    for record in os.walk(dir):
        for f in record[-1]:
            yield os.path.join(record[0], f)


def strftime(fmt, t=None):
    ''' A version of strftime that returns unicode strings and tries to handle dates
    before 1900 '''
    if not fmt:
        return ''
    if t is None:
        t = time.localtime()
    if hasattr(t, 'timetuple'):
        t = t.timetuple()
    early_year = t[0] < 1900
    if early_year:
        replacement = 1900 if t[0]%4 == 0 else 1901
        fmt = fmt.replace('%Y', '_early year hack##')
        t = list(t)
        orig_year = t[0]
        t[0] = replacement
        t = time.struct_time(t)
    ans = None
    if isinstance(fmt, bytes):
        fmt = fmt.decode('utf-8', 'replace')
    ans = time.strftime(fmt, t)
    if early_year:
        ans = ans.replace('_early year hack##', str(orig_year))
    return ans


def my_unichr(num):
    try:
        return safe_chr(num)
    except (ValueError, OverflowError):
        return '?'


XML_ENTITIES = {
    '"': '&quot;',
    "'": '&apos;',
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;'
}


def entity_to_unicode(match, exceptions=(), encoding=None, result_exceptions={}):
    '''
    :param match: A match object such that '&'+match.group(1)';' is the entity.
    :param exceptions: A list of entities to not convert
    :param encoding: The encoding to use to decode numeric entities between 128 and 256.
    :param result_exceptions: A mapping of characters to entities.
    '''
    from calibre.ebooks.html_entities import entity_to_unicode_in_python
    return entity_to_unicode_in_python(match, exceptions, encoding, result_exceptions)


xml_entity_to_unicode = partial(entity_to_unicode, result_exceptions=XML_ENTITIES)


@lru_cache(2)
def entity_regex():
    return re.compile(r'&(\S+?);')


def replace_entities(raw, encoding=None):
    return entity_regex().sub(entity_to_unicode, raw) if raw else raw


def xml_replace_entities(raw, encoding=None):
    return entity_regex().sub(xml_entity_to_unicode, raw) if raw else raw


def prepare_string_for_xml(raw, attribute=False):
    raw = replace_entities(raw)
    raw = raw.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    if attribute:
        raw = raw.replace('"', '&quot;').replace("'", '&apos;')
    return raw


def isbytestring(obj):
    return isinstance(obj, bytes)


def force_unicode(obj, enc=preferred_encoding):
    if isbytestring(obj):
        try:
            obj = obj.decode(enc)
        except Exception:
            try:
                obj = obj.decode(filesystem_encoding if enc ==
                        preferred_encoding else preferred_encoding)
            except Exception:
                try:
                    obj = obj.decode('utf-8')
                except Exception:
                    obj = repr(obj)
                    if isbytestring(obj):
                        obj = obj.decode('utf-8')
    return obj


def as_unicode(obj, enc=preferred_encoding):
    if not isbytestring(obj):
        try:
            obj = str(obj)
        except Exception:
            try:
                obj = str(obj)
            except Exception:
                obj = repr(obj)
    return force_unicode(obj, enc=enc)


def url_slash_cleaner(url):
    '''
    Removes redundant /'s from url's.
    '''
    return re.sub(r'(?<!:)/{2,}', '/', url)


def human_readable(size, sep=' '):
    ''' Convert a size in bytes into a human readable form '''
    divisor, suffix = 1, 'B'
    for i, candidate in enumerate(('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')):
        if size < (1 << ((i + 1) * 10)):
            divisor, suffix = (1 << (i * 10)), candidate
            break
    size = str(float(size)/divisor)
    if size.find('.') > -1:
        size = size[:size.find('.')+2]
    size = size.removesuffix('.0')
    return size + sep + suffix


def fsync(fileobj):
    fileobj.flush()
    os.fsync(fileobj.fileno())


def timed_print(*a, **kw):
    if not is_debugging():
        return
    from time import monotonic
    if not hasattr(timed_print, 'startup_time'):
        timed_print.startup_time = monotonic()
    print(f'[{monotonic() - timed_print.startup_time:.2f}]', *a, **kw)
