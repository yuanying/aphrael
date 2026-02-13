'''Tests for chardet fallback using chardet PyPI package.'''
import unittest


class TestChardet(unittest.TestCase):
    '''Test character encoding detection.'''

    def test_detect_utf8(self):
        from calibre.ebooks.chardet import detect
        raw = 'Hello, World!'.encode('utf-8')
        result = detect(raw)
        self.assertIn('encoding', result)
        self.assertIn('confidence', result)
        self.assertIn(result['encoding'].lower(), ('utf-8', 'ascii'))

    def test_detect_latin1(self):
        from calibre.ebooks.chardet import detect
        raw = 'café résumé'.encode('latin-1')
        result = detect(raw)
        self.assertIn('encoding', result)
        self.assertIsNotNone(result['encoding'])

    def test_detect_str_input(self):
        from calibre.ebooks.chardet import detect
        # String input should be handled gracefully
        result = detect('Hello')
        self.assertIn('encoding', result)

    def test_xml_to_unicode(self):
        from calibre.ebooks.chardet import xml_to_unicode
        raw = b'<?xml version="1.0" encoding="utf-8"?><root>Hello</root>'
        text, encoding = xml_to_unicode(raw)
        self.assertIsInstance(text, str)
        self.assertIn('Hello', text)

    def test_strip_encoding_declarations(self):
        from calibre.ebooks.chardet import strip_encoding_declarations
        raw = '<?xml version="1.0" encoding="utf-8"?><root>Hello</root>'
        result = strip_encoding_declarations(raw)
        self.assertIn('Hello', result)


if __name__ == '__main__':
    unittest.main()
