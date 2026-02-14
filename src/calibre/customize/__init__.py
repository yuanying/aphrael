__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'

import enum
import sys
import zipfile

from calibre.constants import ismacos, iswindows, numeric_version
from calibre.ptempfile import PersistentTemporaryFile

if iswindows:
    platform = 'windows'
elif ismacos:
    platform = 'osx'
else:
    platform = 'linux'


class PluginNotFound(ValueError):
    pass


class InvalidPlugin(ValueError):
    pass


class PluginInstallationType(enum.IntEnum):
    EXTERNAL = 1
    SYSTEM = 2
    BUILTIN = 3


class Plugin:  # {{{
    '''
    A calibre plugin. Useful members include:

       * ``self.installation_type``: Stores how the plugin was installed.
       * ``self.plugin_path``: Stores path to the ZIP file that contains
                               this plugin or None if it is a builtin
                               plugin
       * ``self.site_customization``: Stores a customization string entered
                                      by the user.

    Methods that should be overridden in sub classes:

       * :meth:`initialize`
       * :meth:`customization_help`

    Useful methods:

        * :meth:`temporary_file`
        * :meth:`__enter__`
        * :meth:`load_resources`

    '''
    #: List of platforms this plugin works on.
    #: For example: ``['windows', 'osx', 'linux']``
    supported_platforms = []

    #: The name of this plugin. You must set it something other
    #: than Trivial Plugin for it to work.
    name           = 'Trivial Plugin'

    #: The version of this plugin as a 3-tuple (major, minor, revision)
    version        = (1, 0, 0)

    #: A short string describing what this plugin does
    description    = _('Does absolutely nothing')

    #: The author of this plugin
    author         = _('Unknown')

    #: When more than one plugin exists for a filetype,
    #: the plugins are run in order of decreasing priority.
    #: Plugins with higher priority will be run first.
    #: The highest possible priority is ``sys.maxsize``.
    #: Default priority is 1.
    priority = 1

    #: The earliest version of calibre this plugin requires
    minimum_calibre_version = (0, 4, 118)

    #: The way this plugin is installed
    installation_type  = None

    #: If False, the user will not be able to disable this plugin. Use with
    #: care.
    can_be_disabled = True

    #: The type of this plugin. Used for categorizing plugins in the
    #: GUI
    type = _('Base')

    def __init__(self, plugin_path):
        self.plugin_path        = plugin_path
        self.site_customization = None

    def initialize(self):
        '''
        Called once when calibre plugins are initialized.  Plugins are
        re-initialized every time a new plugin is added. Also note that if the
        plugin is run in a worker process, such as for adding books, then the
        plugin will be initialized for every new worker process.

        Perform any plugin specific initialization here, such as extracting
        resources from the plugin ZIP file. The path to the ZIP file is
        available as ``self.plugin_path``.

        Note that ``self.site_customization`` is **not** available at this point.
        '''
        pass

    def config_widget(self):
        '''
        Implement this method and :meth:`save_settings` in your plugin to
        use a custom configuration dialog, rather then relying on the simple
        string based default customization.

        This method, if implemented, must return a QWidget. The widget can have
        an optional method validate() that takes no arguments and is called
        immediately after the user clicks OK. Changes are applied if and only
        if the method returns True.

        If for some reason you cannot perform the configuration at this time,
        return a tuple of two strings (message, details), these will be
        displayed as a warning dialog to the user and the process will be
        aborted.
        '''
        raise NotImplementedError()

    def save_settings(self, config_widget):
        '''
        Save the settings specified by the user with config_widget.

        :param config_widget: The widget returned by :meth:`config_widget`.

        '''
        raise NotImplementedError()

    def do_user_config(self, parent=None):
        '''
        This method shows a configuration dialog for this plugin. It returns
        True if the user clicks OK, False otherwise. The changes are
        automatically applied.
        '''
        raise NotImplementedError('GUI not available in standalone aphrael')

    def load_resources(self, names):
        '''
        If this plugin comes in a ZIP file (user added plugin), this method
        will allow you to load resources from the ZIP file.

        For example to load an image::

            pixmap = QPixmap()
            pixmap.loadFromData(self.load_resources(['images/icon.png'])['images/icon.png'])
            icon = QIcon(pixmap)

        :param names: List of paths to resources in the ZIP file using / as separator

        :return: A dictionary of the form ``{name: file_contents}``. Any names
                 that were not found in the ZIP file will not be present in the
                 dictionary.

        '''
        if self.plugin_path is None:
            raise ValueError('This plugin was not loaded from a ZIP file')
        ans = {}
        with zipfile.ZipFile(self.plugin_path, 'r') as zf:
            for candidate in zf.namelist():
                if candidate in names:
                    ans[candidate] = zf.read(candidate)
        return ans

    def customization_help(self, gui=False):
        '''
        Return a string giving help on how to customize this plugin.
        By default raise a :class:`NotImplementedError`, which indicates that
        the plugin does not require customization.

        If you re-implement this method in your subclass, the user will
        be asked to enter a string as customization for this plugin.
        The customization string will be available as
        ``self.site_customization``.

        Site customization could be anything, for example, the path to
        a needed binary on the user's computer.

        :param gui: If True return HTML help, otherwise return plain text help.

        '''
        raise NotImplementedError()

    def temporary_file(self, suffix):
        '''
        Return a file-like object that is a temporary file on the file system.
        This file will remain available even after being closed and will only
        be removed on interpreter shutdown. Use the ``name`` member of the
        returned object to access the full path to the created temporary file.

        :param suffix: The suffix that the temporary file will have.
        '''
        return PersistentTemporaryFile(suffix)

    def is_customizable(self):
        try:
            self.customization_help()
            return True
        except NotImplementedError:
            return False

    def __enter__(self, *args):
        '''
        Add this plugin to the python path so that it's contents become directly importable.
        Useful when bundling large python libraries into the plugin. Use it like this::
            with plugin:
                import something
        '''
        if self.plugin_path is not None:
            from importlib.machinery import EXTENSION_SUFFIXES

            from calibre.utils.zipfile import ZipFile
            with ZipFile(self.plugin_path) as zf:
                extensions = {x.lower() for x in EXTENSION_SUFFIXES}
                zip_safe = True
                for name in zf.namelist():
                    for q in extensions:
                        if name.endswith(q):
                            zip_safe = False
                            break
                    if not zip_safe:
                        break
                if zip_safe:
                    sys.path.append(self.plugin_path)
                    self.sys_insertion_path = self.plugin_path
                else:
                    from calibre.ptempfile import TemporaryDirectory
                    self._sys_insertion_tdir = TemporaryDirectory('plugin_unzip')
                    self.sys_insertion_path = self._sys_insertion_tdir.__enter__(*args)
                    zf.extractall(self.sys_insertion_path)
                    sys.path.append(self.sys_insertion_path)

    def __exit__(self, *args):
        ip, it = getattr(self, 'sys_insertion_path', None), getattr(self,
                '_sys_insertion_tdir', None)
        if ip in sys.path:
            sys.path.remove(ip)
        if hasattr(it, '__exit__'):
            it.__exit__(*args)

    def cli_main(self, args):
        '''
        This method is the main entry point for your plugins command line
        interface. It is called when the user does: calibre-debug -r "Plugin
        Name". Any arguments passed are present in the args variable.
        '''
        raise NotImplementedError(f'The {self.name} plugin has no command line interface')

# }}}


class FileTypePlugin(Plugin):  # {{{
    '''
    A plugin that is associated with a particular set of file types.
    '''

    #: Set of file types for which this plugin should be run.
    #: Use '*' for all file types.
    #: For example: ``{'lit', 'mobi', 'prc'}``
    file_types     = set()

    #: If True, this plugin is run when books are added
    #: to the database
    on_import      = False

    #: If True, this plugin is run after books are added
    #: to the database. In this case the postimport and postadd
    #: methods of the plugin are called.
    on_postimport  = False

    #: If True, this plugin is run after a book is converted.
    #: In this case the postconvert method of the plugin is called.
    on_postconvert = False

    #: If True, this plugin is run after a book file is deleted
    #: from the database. In this case the postdelete method of
    #: the plugin is called.
    on_postdelete = False

    #: If True, this plugin is run just before a conversion
    on_preprocess  = False

    #: If True, this plugin is run after conversion
    #: on the final file produced by the conversion output plugin.
    on_postprocess = False

    type = _('File type')

    def run(self, path_to_ebook):
        '''
        Run the plugin. Must be implemented in subclasses.
        It should perform whatever modifications are required
        on the e-book and return the absolute path to the
        modified e-book. If no modifications are needed, it should
        return the path to the original e-book. If an error is encountered
        it should raise an Exception. The default implementation
        simply return the path to the original e-book. Note that the path to
        the original file (before any file type plugins are run, is available as
        self.original_path_to_file).

        The modified e-book file should be created with the
        :meth:`temporary_file` method.

        :param path_to_ebook: Absolute path to the e-book.

        :return: Absolute path to the modified e-book.
        '''
        # Default implementation does nothing
        return path_to_ebook

    def postimport(self, book_id, book_format, db):
        '''
        Called post import, i.e., after the book file has been added to the database. Note that
        this is different from :meth:`postadd` which is called when the book record is created for
        the first time. This method is called whenever a new file is added to a book record. It is
        useful for modifying the book record based on the contents of the newly added file.

        :param book_id: Database id of the added book.
        :param book_format: The file type of the book that was added.
        :param db: Library database.
        '''
        pass  # Default implementation does nothing

    def postconvert(self, book_id, book_format, db):
        '''
        Called post conversion, i.e., after the conversion output book file has been added to the database.
        Note that it is run after a conversion only, not after a book is added. It is useful for modifying
        the book record based on the contents of the newly added file.

        :param book_id: Database id of the added book.
        :param book_format: The file type of the book that was added.
        :param db: Library database.
        '''
        pass  # Default implementation does nothing

    def postdelete(self, book_id, book_format, db):
        '''
        Called post deletion, i.e., after the book file has been deleted from the database. Note
        that it is not run when a book record is deleted, only when one or more formats from the
        book are deleted. It is useful for modifying the book record based on the format of the
        deleted file.

        :param book_id: Database id of the added book.
        :param book_format: The file type of the book that was added.
        :param db: Library database.
        '''
        pass  # Default implementation does nothing

    def postadd(self, book_id, fmt_map, db):
        '''
        Called post add, i.e. after a book has been added to the db. Note that
        this is different from :meth:`postimport`, which is called after a single book file
        has been added to a book. postadd() is called only when an entire book record
        with possibly more than one book file has been created for the first time.
        This is useful if you wish to modify the book record in the database when the
        book is first added to calibre.

        :param book_id: Database id of the added book.
        :param fmt_map: Map of file format to path from which the file format
            was added. Note that this might or might not point to an actual
            existing file, as sometimes files are added as streams. In which case
            it might be a dummy value or a non-existent path.
        :param db: Library database
        '''
        pass  # Default implementation does nothing

# }}}


class MetadataReaderPlugin(Plugin):  # {{{
    '''
    A plugin that implements reading metadata from a set of file types.
    '''
    #: Set of file types for which this plugin should be run.
    #: For example: ``set(['lit', 'mobi', 'prc'])``
    file_types     = set()

    supported_platforms = ['windows', 'osx', 'linux']
    version = numeric_version
    author  = 'Kovid Goyal'

    type = _('Metadata reader')

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.quick = False

    def get_metadata(self, stream, type):
        '''
        Return metadata for the file represented by stream (a file like object
        that supports reading). Raise an exception when there is an error
        with the input data.

        :param type: The type of file. Guaranteed to be one of the entries
            in :attr:`file_types`.
        :return: A :class:`calibre.ebooks.metadata.book.Metadata` object
        '''
        return

# }}}


class MetadataWriterPlugin(Plugin):  # {{{
    '''
    A plugin that implements reading metadata from a set of file types.
    '''
    #: Set of file types for which this plugin should be run.
    #: For example: ``set(['lit', 'mobi', 'prc'])``
    file_types     = set()

    supported_platforms = ['windows', 'osx', 'linux']
    version = numeric_version
    author  = 'Kovid Goyal'

    type = _('Metadata writer')

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.apply_null = False

    def set_metadata(self, stream, mi, type):
        '''
        Set metadata for the file represented by stream (a file like object
        that supports reading). Raise an exception when there is an error
        with the input data.

        :param type: The type of file. Guaranteed to be one of the entries
            in :attr:`file_types`.
        :param mi: A :class:`calibre.ebooks.metadata.book.Metadata` object
        '''
        pass

# }}}
