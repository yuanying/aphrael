__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'

'''
Simplified plugin UI for ebook-converter.
Only conversion-related functions are provided.
'''

import functools
import os
import sys
import traceback
from collections import defaultdict
from itertools import chain, repeat

from calibre.constants import DEBUG
from calibre.customize import FileTypePlugin, MetadataReaderPlugin, MetadataWriterPlugin, PluginInstallationType
from calibre.customize.builtins import plugins as builtin_plugins
from calibre.customize.conversion import InputFormatPlugin, OutputFormatPlugin
from calibre.customize.profiles import InputProfile, OutputProfile
from calibre.utils.config import Config, ConfigProxy

builtin_names = frozenset(p.name for p in builtin_plugins)


def zip_value(iterable, value):
    return zip(iterable, repeat(value))


def _config():
    c = Config('customize')
    c.add_opt('plugins', default={}, help=_('Installed plugins'))
    c.add_opt('filetype_mapping', default={}, help=_('Mapping for filetype plugins'))
    c.add_opt('plugin_customization', default={}, help=_('Local plugin customization'))
    c.add_opt('disabled_plugins', default=set(), help=_('Disabled plugins'))
    c.add_opt('enabled_plugins', default=set(), help=_('Enabled plugins'))

    return ConfigProxy(c)


config = _config()


def find_plugin(name):
    for plugin in _initialized_plugins:
        if plugin.name == name:
            return plugin


default_disabled_plugins = set()


def is_disabled(plugin_or_name):
    name = getattr(plugin_or_name, 'name', plugin_or_name)
    if name in config['enabled_plugins']:
        return False
    return name in config['disabled_plugins'] or name in default_disabled_plugins


# File type plugins {{{

_on_import           = {}
_on_postimport       = {}
_on_postconvert      = {}
_on_postdelete       = {}
_on_preprocess       = {}
_on_postprocess      = {}
_on_postadd          = []


def reread_filetype_plugins():
    global _on_import, _on_postimport, _on_postconvert, _on_postdelete, _on_preprocess, _on_postprocess, _on_postadd
    _on_import           = defaultdict(list)
    _on_postimport       = defaultdict(list)
    _on_postconvert      = defaultdict(list)
    _on_postdelete       = defaultdict(list)
    _on_preprocess       = defaultdict(list)
    _on_postprocess      = defaultdict(list)
    _on_postadd          = []

    for plugin in _initialized_plugins:
        if isinstance(plugin, FileTypePlugin):
            for ft in plugin.file_types:
                if plugin.on_import:
                    _on_import[ft].append(plugin)
                if plugin.on_postimport:
                    _on_postimport[ft].append(plugin)
                    _on_postadd.append(plugin)
                if plugin.on_postconvert:
                    _on_postconvert[ft].append(plugin)
                if plugin.on_postdelete:
                    _on_postdelete[ft].append(plugin)
                if plugin.on_preprocess:
                    _on_preprocess[ft].append(plugin)
                if plugin.on_postprocess:
                    _on_postprocess[ft].append(plugin)


def plugins_for_ft(ft, occasion):
    op = {
        'import':_on_import, 'preprocess':_on_preprocess, 'postprocess':_on_postprocess, 'postimport':_on_postimport,
        'postconvert':_on_postconvert, 'postdelete':_on_postdelete,
    }[occasion]
    for p in chain(op.get(ft, ()), op.get('*', ())):
        if not is_disabled(p):
            yield p


def _run_filetype_plugins(path_to_file, ft=None, occasion='preprocess'):
    customization = config['plugin_customization']
    if ft is None:
        ft = os.path.splitext(path_to_file)[-1].lower().replace('.', '')
    nfp = path_to_file
    for plugin in plugins_for_ft(ft, occasion):
        plugin.site_customization = customization.get(plugin.name, '')
        oo, oe = sys.stdout, sys.stderr
        with plugin:
            try:
                plugin.original_path_to_file = path_to_file
            except Exception:
                pass
            try:
                nfp = plugin.run(nfp) or nfp
            except Exception:
                print(f'Running file type plugin {plugin.name} failed with traceback:', file=oe)
                traceback.print_exc(file=oe)
        sys.stdout, sys.stderr = oo, oe
    import shutil
    def x(j):
        return os.path.normpath(os.path.normcase(j))
    if occasion == 'postprocess' and x(nfp) != x(path_to_file):
        shutil.copyfile(nfp, path_to_file)
        nfp = path_to_file
    return nfp


run_plugins_on_import      = functools.partial(_run_filetype_plugins, occasion='import')
run_plugins_on_preprocess  = functools.partial(_run_filetype_plugins, occasion='preprocess')
run_plugins_on_postprocess = functools.partial(_run_filetype_plugins, occasion='postprocess')

# }}}


# Plugin customization {{{

def customize_plugin(plugin, custom):
    d = config['plugin_customization']
    d[plugin.name] = custom.strip()
    config['plugin_customization'] = d


def plugin_customization(plugin):
    return config['plugin_customization'].get(plugin.name, '')

# }}}


# Input/Output profiles {{{

def input_profiles():
    for plugin in _initialized_plugins:
        if isinstance(plugin, InputProfile):
            yield plugin


def output_profiles():
    for plugin in _initialized_plugins:
        if isinstance(plugin, OutputProfile):
            yield plugin
# }}}


# Metadata plugins {{{

_metadata_readers = {}
_metadata_writers = {}


def reread_metadata_plugins():
    global _metadata_readers, _metadata_writers
    _metadata_readers = defaultdict(list)
    _metadata_writers = defaultdict(list)
    for plugin in _initialized_plugins:
        if isinstance(plugin, MetadataReaderPlugin):
            for ft in plugin.file_types:
                _metadata_readers[ft].append(plugin)
        elif isinstance(plugin, MetadataWriterPlugin):
            for ft in plugin.file_types:
                _metadata_writers[ft].append(plugin)


def metadata_readers():
    for plugin in _initialized_plugins:
        if isinstance(plugin, MetadataReaderPlugin):
            yield plugin


def metadata_writers():
    for plugin in _initialized_plugins:
        if isinstance(plugin, MetadataWriterPlugin):
            yield plugin

# }}}


# Input/Output format plugins {{{

def input_format_plugins():
    for plugin in _initialized_plugins:
        if isinstance(plugin, InputFormatPlugin):
            yield plugin


def plugin_for_input_format(fmt):
    customization = config['plugin_customization']
    for plugin in input_format_plugins():
        if fmt.lower() in plugin.file_types:
            plugin.site_customization = customization.get(plugin.name, None)
            return plugin


def all_input_formats():
    formats = set()
    for plugin in input_format_plugins():
        for format in plugin.file_types:
            formats.add(format)
    return formats


def available_input_formats():
    formats = set()
    for plugin in input_format_plugins():
        if not is_disabled(plugin):
            for format in plugin.file_types:
                formats.add(format)
    return formats


def output_format_plugins():
    for plugin in _initialized_plugins:
        if isinstance(plugin, OutputFormatPlugin):
            yield plugin


def plugin_for_output_format(fmt):
    customization = config['plugin_customization']
    for plugin in output_format_plugins():
        if fmt.lower() == plugin.file_type:
            plugin.site_customization = customization.get(plugin.name, None)
            return plugin


def available_output_formats():
    formats = set()
    for plugin in output_format_plugins():
        if not is_disabled(plugin):
            formats.add(plugin.file_type)
    return formats

# }}}


# Plugin initialization {{{

_initialized_plugins = []


def initialize_plugin(plugin, path_to_zip_file, installation_type):
    if isinstance(plugin, type):
        plugin = plugin(path_to_zip_file)
    plugin.installation_type = installation_type
    if hasattr(plugin, 'initialize'):
        plugin.initialize()
    return plugin


def initialize_plugins(perf=False):
    global _initialized_plugins
    _initialized_plugins = []

    for zfp, installation_type in zip_value(builtin_plugins, PluginInstallationType.BUILTIN):
        try:
            plugin = initialize_plugin(
                    zfp,
                    None, installation_type,
            )
            _initialized_plugins.append(plugin)
        except Exception:
            print('Failed to initialize plugin:', repr(zfp), file=sys.stderr)
            if DEBUG:
                traceback.print_exc()
    _initialized_plugins.sort(key=lambda x: x.priority, reverse=True)
    reread_filetype_plugins()
    reread_metadata_plugins()


initialize_plugins()


def initialized_plugins():
    yield from _initialized_plugins

# }}}


def all_metadata_plugins():
    '''Stub: Returns empty list - no metadata download plugins available.'''
    return []


def metadata_plugins(capabilities):
    '''Stub: Returns empty list - no metadata download plugins available.'''
    return []
