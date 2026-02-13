__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal kovid@kovidgoyal.net'
__docformat__ = 'restructuredtext en'

'''
Perform various initialization tasks - simplified for standalone package.
'''

import builtins
import locale
import os

# Default translation is NOOP
builtins.__dict__['_'] = lambda s: s

# For strings which belong in the translation tables, but which shouldn't be
# immediately translated to the environment language
builtins.__dict__['__'] = lambda s: s

# For backwards compat with some third party plugins
builtins.__dict__['dynamic_property'] = lambda func: func(None)


def initialize_calibre():
    if hasattr(initialize_calibre, 'initialized'):
        return
    initialize_calibre.initialized = True
    # Ensure that all temp files/dirs are created under a calibre tmp dir
    from calibre.ptempfile import fix_tempfile_module
    fix_tempfile_module()

    #
    # Setup resources
    from calibre.utils import resources
    resources

    #
    # Setup translations
    from calibre.utils.localization import getlangcode_from_envvars, set_translators

    set_translators()

    #
    # Initialize locale
    import string
    string
    try:
        locale.setlocale(locale.LC_ALL, '')
    except Exception:
        try:
            dl = getlangcode_from_envvars()
            if dl:
                locale.setlocale(locale.LC_ALL, dl)
        except Exception:
            pass

    builtins.__dict__['lopen'] = open  # legacy compatibility
    from calibre.utils.icu import lower as icu_lower
    from calibre.utils.icu import title_case
    from calibre.utils.icu import upper as icu_upper
    builtins.__dict__['icu_lower'] = icu_lower
    builtins.__dict__['icu_upper'] = icu_upper
    builtins.__dict__['icu_title'] = title_case

    # Remove connect_lambda since we don't have Qt
    builtins.__dict__['connect_lambda'] = lambda *a, **kw: None


def get_debug_executable(headless=False, exe_name='calibre-debug'):
    import sys
    nearby = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), exe_name)
    if os.path.exists(nearby):
        return [nearby]
    return [exe_name]
