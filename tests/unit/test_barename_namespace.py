'''Tests for barename/namespace Python implementations (speedup replacements).'''
import unittest


class TestBarenameNamespace(unittest.TestCase):
    '''Test pure Python barename and namespace functions.'''

    def test_barename_with_namespace(self):
        from calibre.ebooks.oeb.parse_utils import barename
        self.assertEqual(barename('{http://www.w3.org/1999/xhtml}div'), 'div')
        self.assertEqual(barename('{http://example.com}span'), 'span')

    def test_barename_without_namespace(self):
        from calibre.ebooks.oeb.parse_utils import barename
        self.assertEqual(barename('div'), 'div')
        self.assertEqual(barename('p'), 'p')

    def test_barename_empty(self):
        from calibre.ebooks.oeb.parse_utils import barename
        self.assertEqual(barename(''), '')

    def test_namespace_with_namespace(self):
        from calibre.ebooks.oeb.parse_utils import namespace
        self.assertEqual(namespace('{http://www.w3.org/1999/xhtml}div'), 'http://www.w3.org/1999/xhtml')
        self.assertEqual(namespace('{http://example.com}span'), 'http://example.com')

    def test_namespace_without_namespace(self):
        from calibre.ebooks.oeb.parse_utils import namespace
        self.assertEqual(namespace('div'), '')
        self.assertEqual(namespace('p'), '')

    def test_namespace_empty(self):
        from calibre.ebooks.oeb.parse_utils import namespace
        self.assertEqual(namespace(''), '')


if __name__ == '__main__':
    unittest.main()
