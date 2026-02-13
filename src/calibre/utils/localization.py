#!/usr/bin/env python
# License: GPLv3 Copyright: 2009, Kovid Goyal <kovid at kovidgoyal.net>

'''
Simplified localization module - English only (NOP Translator).
'''

import locale
import os
import re

_available_translations = None
default_envvars_for_langcode = ('LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LC_MESSAGES', 'LANG')


def available_translations():
    return []


def getlangcode_from_envvars(envvars=default_envvars_for_langcode):
    lookup = os.environ.get
    for k in envvars:
        localename = lookup(k)
        if localename:
            if k == 'LANGUAGE':
                localename = localename.split(':')[0]
            break
    else:
        localename = 'C'
    return locale._parse_localename(localename)[0]


def get_system_locale():
    lang = None
    try:
        lang = getlangcode_from_envvars()
        if lang is None:
            for var in default_envvars_for_langcode:
                if os.environ.get(var) == 'C':
                    lang = 'en_US'
                    break
    except Exception:
        pass
    if lang is None and 'LANG' in os.environ:
        try:
            lang = os.environ['LANG']
        except Exception:
            pass
    if lang:
        lang = lang.replace('-', '_')
        lang = '_'.join(lang.split('_')[:2])
    return lang


def sanitize_lang(lang):
    if lang:
        match = re.match(r'[a-z]{2,3}(_[A-Z]{2}){0,1}', lang)
        if match:
            lang = match.group()
    if lang == 'zh':
        lang = 'zh_CN'
    if not lang:
        lang = 'en'
    return lang


def get_lang():
    'Try to figure out what language to display the interface in'
    from calibre.utils.config_base import prefs
    lang = prefs['language']
    lang = os.environ.get('CALIBRE_OVERRIDE_LANG', lang)
    if lang:
        return lang
    try:
        lang = get_system_locale()
    except Exception:
        lang = None
    return sanitize_lang(lang)


def is_rtl():
    return get_lang()[:2].lower() in {'he', 'ar'}


lcdata = {
    'abday': ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'),
    'abmon': ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
    'd_fmt': '%m/%d/%Y',
    'd_t_fmt': '%a %d %b %Y %r %Z',
    'day': ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'),
    'mon': ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'),
    'noexpr': '^[nN].*',
    'radixchar': '.',
    't_fmt': '%r',
    't_fmt_ampm': '%I:%M:%S %p',
    'thousep': ',',
    'yesexpr': '^[yY].*'
}


class NOPTranslator:
    '''NOP Translator - returns strings as-is (English only).'''

    def gettext(self, msg):
        return msg

    def ngettext(self, singular, plural, n):
        return singular if n == 1 else plural

    def pgettext(self, context, msg):
        return msg

    def install(self, names=None):
        import builtins
        builtins.__dict__['_'] = self.gettext
        if names and 'ngettext' in names:
            builtins.__dict__['ngettext'] = self.ngettext

    def info(self):
        return {'language': 'en'}

    def set_as_qt_translator(self):
        return b''

    def add_fallback(self, translator):
        pass


default_translator = NOPTranslator()


def _(x: str) -> str:
    return default_translator.gettext(x)


def __(x: str) -> str:
    return x


def ngettext(singular: str, plural: str, n: int) -> str:
    return default_translator.ngettext(singular, plural, n)


def pgettext(context: str, msg: str) -> str:
    return default_translator.pgettext(context, msg)


def set_translators():
    global default_translator
    default_translator = NOPTranslator()
    default_translator.install(names=('ngettext',))
    from calibre.utils.config_base import prefs
    prefs.retranslate_help()


set_translators.lang = None

_extra_lang_codes = {
    'pt_BR': 'Brazilian Portuguese',
    'zh_CN': 'Simplified Chinese',
    'zh_TW': 'Traditional Chinese',
    'bn_IN': 'Indian Bengali',
    'bn_BD': 'Bangladeshi Bengali',
    'en'   : 'English',
    'und'  : 'Unknown'
}

_lcase_map = {}
for k in _extra_lang_codes:
    _lcase_map[k.lower()] = k


def canonicalize_lang(raw):
    if not raw:
        return None
    if not isinstance(raw, str):
        raw = raw.decode('utf-8', 'ignore')
    raw = raw.lower().strip()
    if not raw:
        return None
    raw = raw.replace('_', '-').partition('-')[0].strip()
    if not raw:
        return None
    # Simplified: just return the raw lang code
    if len(raw) == 2:
        # Common 2-to-3 letter mappings
        m = {'en': 'eng', 'fr': 'fra', 'de': 'deu', 'es': 'spa', 'it': 'ita',
             'ja': 'jpn', 'zh': 'zho', 'ko': 'kor', 'pt': 'por', 'ru': 'rus',
             'ar': 'ara', 'he': 'heb', 'nl': 'nld', 'sv': 'swe', 'da': 'dan',
             'no': 'nor', 'fi': 'fin', 'pl': 'pol', 'cs': 'ces', 'hu': 'hun',
             'ro': 'ron', 'tr': 'tur', 'uk': 'ukr', 'el': 'ell', 'th': 'tha',
             'vi': 'vie', 'id': 'ind', 'ms': 'msa', 'hi': 'hin', 'bn': 'ben'}
        return m.get(raw, None)
    elif len(raw) == 3:
        return raw
    return None


def lang_as_iso639_1(name_or_code):
    code = canonicalize_lang(name_or_code)
    if code is not None:
        m = {'eng': 'en', 'fra': 'fr', 'deu': 'de', 'spa': 'es', 'ita': 'it',
             'jpn': 'ja', 'zho': 'zh', 'kor': 'ko', 'por': 'pt', 'rus': 'ru',
             'ara': 'ar', 'heb': 'he', 'nld': 'nl', 'swe': 'sv', 'dan': 'da',
             'nor': 'no', 'fin': 'fi', 'pol': 'pl', 'ces': 'cs', 'hun': 'hu',
             'ron': 'ro', 'tur': 'tr', 'ukr': 'uk', 'ell': 'el', 'tha': 'th',
             'vie': 'vi', 'ind': 'id', 'msa': 'ms', 'hin': 'hi', 'ben': 'bn'}
        return m.get(code, None)


def get_language(lang, gettext_func=None):
    lang = _lcase_map.get(lang, lang)
    if lang in _extra_lang_codes:
        return _extra_lang_codes[lang]
    return lang


def calibre_langcode_to_name(lc, localize=True):
    return lc


def get_udc():
    return None
