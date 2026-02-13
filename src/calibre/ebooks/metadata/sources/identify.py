#!/usr/bin/env python
# License: GPLv3 Copyright: 2011, Kovid Goyal <kovid at kovidgoyal.net>

'''
Minimal stub for urls_from_identifiers.
'''

import re
from urllib.parse import urlparse


def urls_from_identifiers(identifiers, sort_results=False):
    '''Generate URLs from book identifiers (isbn, doi, etc).'''
    identifiers = {k.lower(): v for k, v in identifiers.items()}
    ans = []

    def add(name, k, val, url):
        ans.append((name, k, val, url))

    isbn = identifiers.get('isbn', None)
    if isbn:
        add(isbn, 'isbn', isbn, 'https://www.worldcat.org/isbn/' + isbn)
    doi = identifiers.get('doi', None)
    if doi:
        add('DOI', 'doi', doi, 'https://dx.doi.org/' + doi)
    arxiv = identifiers.get('arxiv', None)
    if arxiv:
        add('arXiv', 'arxiv', arxiv, 'https://arxiv.org/abs/' + arxiv)
    oclc = identifiers.get('oclc', None)
    if oclc:
        add('OCLC', 'oclc', oclc, 'https://www.worldcat.org/oclc/' + oclc)

    q = {'http', 'https', 'file'}
    for k, url in identifiers.items():
        if url and re.match(r'ur[il]\d*$', k) is not None:
            url = url[:8].replace('|', ':') + url[8:].replace('|', ',')
            if url.partition(':')[0].lower() in q:
                parts = urlparse(url)
                name = parts.netloc or parts.path
                add(name, k, url, url)

    return ans
