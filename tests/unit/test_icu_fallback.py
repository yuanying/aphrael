'''Tests for ICU fallback implementation using Python stdlib.'''
import unittest


class TestICUFallback(unittest.TestCase):
    '''Test the pure Python ICU replacement functions.'''

    def test_lower(self):
        from calibre.utils.icu import lower
        self.assertEqual(lower('ABC'), 'abc')
        self.assertEqual(lower('Hello World'), 'hello world')
        self.assertEqual(lower(''), '')
        self.assertEqual(lower(None), None)

    def test_upper(self):
        from calibre.utils.icu import upper
        self.assertEqual(upper('abc'), 'ABC')
        self.assertEqual(upper('Hello World'), 'HELLO WORLD')
        self.assertEqual(upper(''), '')
        self.assertEqual(upper(None), None)

    def test_capitalize(self):
        from calibre.utils.icu import capitalize
        self.assertEqual(capitalize('hello world'), 'Hello world')
        self.assertEqual(capitalize(''), '')
        self.assertEqual(capitalize(None), None)

    def test_swapcase(self):
        from calibre.utils.icu import swapcase
        self.assertEqual(swapcase('Hello World'), 'hELLO wORLD')
        self.assertEqual(swapcase(''), '')
        self.assertEqual(swapcase(None), None)

    def test_sort_key(self):
        from calibre.utils.icu import sort_key
        # sort_key should return bytes
        sk = sort_key('hello')
        self.assertIsInstance(sk, bytes)
        # Empty and None cases
        self.assertEqual(sort_key(None), b'')
        self.assertEqual(sort_key(''), b'')
        # Sort order should be case-insensitive
        self.assertEqual(sort_key('abc'), sort_key('ABC'))

    def test_strcmp(self):
        from calibre.utils.icu import strcmp
        self.assertEqual(strcmp('a', 'a'), 0)
        self.assertLess(strcmp('a', 'b'), 0)
        self.assertGreater(strcmp('b', 'a'), 0)
        # Case insensitive by default
        self.assertEqual(strcmp('a', 'A'), 0)
        # None handling
        self.assertEqual(strcmp(None, ''), 0)
        self.assertEqual(strcmp(None, None), 0)

    def test_normalize(self):
        import unicodedata

        from calibre.utils.icu import normalize
        # NFC normalization
        decomposed = 'e\u0301'  # e + combining accent
        self.assertEqual(normalize(decomposed), unicodedata.normalize('NFC', decomposed))

    def test_safe_chr(self):
        from calibre.utils.icu import safe_chr
        self.assertEqual(safe_chr(65), 'A')
        self.assertEqual(safe_chr(0x1f431), '\U0001f431')

    def test_contractions(self):
        from calibre.utils.icu import contractions
        result = contractions()
        self.assertIsInstance(result, frozenset)

    def test_string_length(self):
        from calibre.utils.icu import string_length
        self.assertEqual(string_length('hello'), 5)
        self.assertEqual(string_length(''), 0)


if __name__ == '__main__':
    unittest.main()
