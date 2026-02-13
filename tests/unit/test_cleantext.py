'''Tests for cleantext module with Python fallback for speedup C extension.'''
import unittest


class TestCleanText(unittest.TestCase):
    '''Test clean_xml_chars and related functions.'''

    def test_clean_xml_chars(self):
        from calibre.utils.cleantext import clean_xml_chars
        raw = 'asd\x02a\U00010437x\ud801b\udffe\ud802'
        result = clean_xml_chars(raw)
        self.assertEqual(result, 'asda\U00010437xb')

    def test_clean_xml_chars_preserves_valid(self):
        from calibre.utils.cleantext import clean_xml_chars
        valid = 'Hello World\n\t\r'
        self.assertEqual(clean_xml_chars(valid), valid)

    def test_clean_xml_chars_empty(self):
        from calibre.utils.cleantext import clean_xml_chars
        self.assertEqual(clean_xml_chars(''), '')

    def test_clean_ascii_chars(self):
        from calibre.utils.cleantext import clean_ascii_chars
        txt = 'hello\x00\x01world'
        result = clean_ascii_chars(txt)
        self.assertEqual(result, 'helloworld')
        # Should preserve tab, newline, carriage return
        txt2 = 'hello\t\n\rworld'
        self.assertEqual(clean_ascii_chars(txt2), txt2)

    def test_unescape(self):
        from calibre.utils.cleantext import unescape
        self.assertEqual(unescape('&amp;'), '&')
        self.assertEqual(unescape('&lt;'), '<')
        self.assertEqual(unescape('&#65;'), 'A')
        self.assertEqual(unescape('&#x41;'), 'A')


if __name__ == '__main__':
    unittest.main()
