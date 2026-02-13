#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2010, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

'''
Pure Python replacement for calibre_extensions.icu.
Uses unicodedata + locale + str methods.
'''

import locale
import unicodedata

from polyglot.builtins import cmp

_locale = None
icu_unicode_version = unicodedata.unidata_version


def change_locale(lang=None):
    global _locale
    _locale = lang


def _get_locale():
    global _locale
    if _locale is None:
        _locale = 'en'
    return _locale


def normalize(text, mode='NFC'):
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    return unicodedata.normalize(mode, text)


def _ensure_str(x):
    if x is None:
        return None
    if isinstance(x, bytes):
        return x.decode('utf-8', 'replace')
    return x


def lower(x):
    x = _ensure_str(x)
    if not x or not isinstance(x, str):
        return x
    return x.lower()


def upper(x):
    x = _ensure_str(x)
    if not x or not isinstance(x, str):
        return x
    return x.upper()


def title_case(x):
    x = _ensure_str(x)
    if not x or not isinstance(x, str):
        return x
    return x.title()


def capitalize(x):
    x = _ensure_str(x)
    if not x or not isinstance(x, str):
        return x
    return x[0].upper() + x[1:].lower()


def swapcase(x):
    x = _ensure_str(x)
    if not x or not isinstance(x, str):
        return x
    return x.swapcase()


def sort_key(x):
    if x is None:
        return b''
    if isinstance(x, bytes):
        try:
            x = x.decode('utf-8')
        except UnicodeDecodeError:
            return x
    if not x:
        return b''
    try:
        return locale.strxfrm(x.casefold()).encode('utf-8', 'replace')
    except Exception:
        return x.casefold().encode('utf-8', 'replace')


def numeric_sort_key(x):
    '''Sort key that handles embedded numbers naturally.'''
    import re
    if x is None:
        return b''
    if isinstance(x, bytes):
        try:
            x = x.decode('utf-8')
        except UnicodeDecodeError:
            return x
    if not x:
        return b''
    parts = re.split(r'(\d+)', x.casefold())
    result = []
    for part in parts:
        if part.isdigit():
            result.append(int(part).to_bytes(8, 'big'))
        else:
            try:
                result.append(locale.strxfrm(part).encode('utf-8', 'replace'))
            except Exception:
                result.append(part.encode('utf-8', 'replace'))
    return b'\0'.join(result)


def case_sensitive_sort_key(x):
    if x is None:
        return b''
    if isinstance(x, bytes):
        try:
            x = x.decode('utf-8')
        except UnicodeDecodeError:
            return x
    if not x:
        return b''
    try:
        return locale.strxfrm(x).encode('utf-8', 'replace')
    except Exception:
        return x.encode('utf-8', 'replace')


def primary_sort_key(x):
    '''Sort key ignoring case and accents.'''
    if x is None:
        return b''
    if isinstance(x, bytes):
        try:
            x = x.decode('utf-8')
        except UnicodeDecodeError:
            return x
    if not x:
        return b''
    # Strip accents via NFD decomposition
    stripped = ''.join(c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn')
    return sort_key(stripped)


def strcmp(a, b):
    a = _ensure_str(a) or ''
    b = _ensure_str(b) or ''
    a_lower = a.casefold()
    b_lower = b.casefold()
    return cmp(a_lower, b_lower)


def case_sensitive_strcmp(a, b):
    a = _ensure_str(a) or ''
    b = _ensure_str(b) or ''
    return cmp(a, b)


def primary_strcmp(a, b):
    '''Compare ignoring case and accents.'''
    a = _ensure_str(a) or ''
    b = _ensure_str(b) or ''

    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return strcmp(strip_accents(a), strip_accents(b))


def find(needle, haystack):
    if isinstance(needle, bytes):
        needle = needle.decode('utf-8', 'replace')
    if isinstance(haystack, bytes):
        haystack = haystack.decode('utf-8', 'replace')
    idx = haystack.find(needle)
    if idx == -1:
        return -1, -1
    return idx, len(needle)


def primary_find(needle, haystack):
    return find(needle, haystack)


def contains(needle, haystack):
    if isinstance(needle, bytes):
        needle = needle.decode('utf-8', 'replace')
    if isinstance(haystack, bytes):
        haystack = haystack.decode('utf-8', 'replace')
    return needle.lower() in haystack.lower()


def primary_contains(needle, haystack):
    return contains(needle, haystack)


def startswith(a, b):
    if isinstance(a, bytes):
        a = a.decode('utf-8', 'replace')
    if isinstance(b, bytes):
        b = b.decode('utf-8', 'replace')
    return a.lower().startswith(b.lower())


def primary_startswith(a, b):
    return startswith(a, b)


def safe_chr(num):
    return chr(num)


def contractions():
    return frozenset()


def string_length(x):
    if x is None:
        return 0
    if isinstance(x, bytes):
        x = x.decode('utf-8', 'replace')
    return len(x)


def collation_order(x):
    if not x:
        return 0, ''
    return ord(x[0]), x[0]


def make_sort_key_func(collator_func, func='sort_key'):
    collator_func()  # Call for compatibility, result unused
    return sort_key


def make_two_arg_func(collator_func, func='strcmp'):
    return strcmp


def make_change_case_func(collator_func, func='lower'):
    funcs = {'lower': lower, 'upper': upper, 'title': title_case, 'capitalize': capitalize, 'swapcase': swapcase}
    return funcs.get(func, lower)
