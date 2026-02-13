__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'

'''
Builtin plugins for ebook-converter.
Only EPUB/MOBI/AZW3 metadata and conversion plugins are registered.
'''


from calibre.customize import MetadataReaderPlugin, MetadataWriterPlugin

# Metadata reader plugins {{{


class EPUBMetadataReader(MetadataReaderPlugin):

    name        = 'Read EPUB metadata'
    file_types  = {'epub'}
    description = _('Read metadata from EPUB files')

    def get_metadata(self, stream, ftype):
        from calibre.ebooks.metadata.epub import get_metadata, get_quick_metadata
        if self.quick:
            return get_quick_metadata(stream, ftype=ftype)
        return get_metadata(stream, ftype=ftype)


class MOBIMetadataReader(MetadataReaderPlugin):

    name        = 'Read MOBI metadata'
    file_types  = {'mobi', 'prc', 'azw', 'azw3', 'azw4', 'pobi'}
    description = _('Read metadata from %s files') % 'MOBI'

    def get_metadata(self, stream, ftype):
        from calibre.ebooks.metadata.mobi import get_metadata
        return get_metadata(stream)


class OPFMetadataReader(MetadataReaderPlugin):

    name        = 'Read OPF metadata'
    file_types  = {'opf'}
    description = _('Read metadata from %s files') % 'OPF'

    def get_metadata(self, stream, ftype):
        from calibre.ebooks.metadata.opf2 import OPF
        return OPF(stream, populate_spine=False, try_resolve_media_types=False).to_book_metadata()

# }}}


# Metadata writer plugins {{{

class EPUBMetadataWriter(MetadataWriterPlugin):

    name        = 'Set EPUB metadata'
    file_types  = {'epub'}
    description = _('Set metadata in %s files') % 'EPUB'

    def set_metadata(self, stream, mi, type):
        from calibre.ebooks.metadata.epub import set_metadata
        q = mi.to_book_metadata() if hasattr(mi, 'to_book_metadata') else mi
        set_metadata(stream, q, apply_null=self.apply_null, force_identifiers=self.force_identifiers)

    def __init__(self, *args, **kwargs):
        MetadataWriterPlugin.__init__(self, *args, **kwargs)
        self.force_identifiers = False


class MOBIMetadataWriter(MetadataWriterPlugin):

    name        = 'Set MOBI metadata'
    file_types  = {'mobi', 'prc', 'azw', 'azw3'}
    description = _('Set metadata in %s files') % 'MOBI'

    def set_metadata(self, stream, mi, type):
        from calibre.ebooks.metadata.mobi import set_metadata
        set_metadata(stream, mi)

# }}}


# Conversion input/output plugins {{{

# }}}
# OEB Output plugin {{{
from calibre.customize.conversion import OutputFormatPlugin
from calibre.ebooks.conversion.plugins.epub_input import EPUBInput
from calibre.ebooks.conversion.plugins.epub_output import EPUBOutput
from calibre.ebooks.conversion.plugins.mobi_input import MOBIInput
from calibre.ebooks.conversion.plugins.mobi_output import AZW3Output, MOBIOutput


class OEBOutput(OutputFormatPlugin):

    name = 'OEB Output'
    author = 'Kovid Goyal'
    file_type = 'oeb'
    commit_name = 'oeb_output'

    recommendations = set()

    def convert(self, oeb_book, output_path, input_plugin, opts, log):
        from calibre.ebooks.oeb.writer import OEBWriter
        writer = OEBWriter()
        writer(oeb_book, output_path)

# }}}


from calibre.customize.profiles import input_profiles, output_profiles

plugins = [
    EPUBMetadataReader,
    MOBIMetadataReader,
    OPFMetadataReader,
    EPUBMetadataWriter,
    MOBIMetadataWriter,
    EPUBInput,
    EPUBOutput,
    MOBIInput,
    MOBIOutput,
    AZW3Output,
    OEBOutput,
] + list(input_profiles) + list(output_profiles)
