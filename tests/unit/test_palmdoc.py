'''Tests for PalmDoc compression/decompression Python implementation.'''
import unittest


class TestPalmDoc(unittest.TestCase):
    '''Test the pure Python PalmDoc compression and decompression.'''

    def test_compress_decompress_roundtrip(self):
        from calibre.ebooks.compression.palmdoc import compress_doc, decompress_doc
        test_cases = [
            b'abc\x03\x04\x05\x06ms',  # Binary writing
            b'a b c \xfed ',  # Encoding of spaces
            b'0123456789axyz2bxyz2cdfgfo9iuyerh',
            b'0123456789asd0123456789asd|yyzzxxffhhjjkk',
            (b'ciewacnaq eiu743 r787q 0w%  ; sa fd\xef\ffdxosac wocjp acoiecowei '
             b'owaic jociowapjcivcjpoivjporeivjpoavca; p9aw8743y6r74%$^$^%8 '),
        ]
        for data in test_cases:
            compressed = compress_doc(data)
            decompressed = decompress_doc(compressed)
            self.assertEqual(decompressed, data, f'Round-trip failed for: {data!r}')

    def test_compress_empty(self):
        from calibre.ebooks.compression.palmdoc import compress_doc
        self.assertEqual(compress_doc(b''), b'')

    def test_decompress_empty(self):
        from calibre.ebooks.compression.palmdoc import decompress_doc
        self.assertEqual(decompress_doc(b''), b'')

    def test_py_compress_matches(self):
        '''Verify py_compress_doc matches compress_doc output.'''
        from calibre.ebooks.compression.palmdoc import compress_doc, py_compress_doc
        test_data = b'0123456789asd0123456789asd|yyzzxxffhhjjkk'
        self.assertEqual(py_compress_doc(test_data), compress_doc(test_data))


if __name__ == '__main__':
    unittest.main()
