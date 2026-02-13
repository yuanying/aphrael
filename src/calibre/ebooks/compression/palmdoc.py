#!/usr/bin/env python


__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'

import io
from struct import pack


def decompress_doc(data):
    '''Pure Python PalmDoc decompression.'''
    if not data:
        return b''
    out = io.BytesIO()
    i = 0
    ldata = len(data)
    while i < ldata:
        c = data[i]
        i += 1
        if c >= 1 and c <= 8:
            # Copy next c bytes literally
            out.write(data[i:i+c])
            i += c
        elif c <= 0x7f:
            # Literal byte
            out.write(bytes([c]))
        elif c >= 0xc0:
            # Space + (c ^ 0x80)
            out.write(b' ')
            out.write(bytes([c ^ 0x80]))
        else:
            # LZ77 distance-length pair
            if i >= ldata:
                break
            c = (c << 8) | data[i]
            i += 1
            distance = (c >> 3) & 0x7ff
            length = (c & 0x07) + 3
            buf = out.getvalue()
            pos = len(buf) - distance
            for j in range(length):
                if pos + j >= 0 and pos + j < len(buf):
                    out.write(bytes([buf[pos + j]]))
                else:
                    out.write(b'\x00')
    return out.getvalue()


def compress_doc(data):
    return py_compress_doc(data) if data else b''


def py_compress_doc(data):
    out = io.BytesIO()
    i = 0
    ldata = len(data)
    while i < ldata:
        if i > 10 and (ldata - i) > 10:
            chunk = b''
            match = -1
            for j in range(10, 2, -1):
                chunk = data[i:i+j]
                try:
                    match = data.rindex(chunk, 0, i)
                except ValueError:
                    continue
                if (i - match) <= 2047:
                    break
                match = -1
            if match >= 0:
                n = len(chunk)
                m = i - match
                code = 0x8000 + ((m << 3) & 0x3ff8) + (n - 3)
                out.write(pack('>H', code))
                i += n
                continue
        ch = data[i:i+1]
        och = ord(ch)
        i += 1
        if ch == b' ' and (i + 1) < ldata:
            onch = ord(data[i:i+1])
            if onch >= 0x40 and onch < 0x80:
                out.write(pack('>B', onch ^ 0x80))
                i += 1
                continue
        if och == 0 or (och > 8 and och < 0x80):
            out.write(ch)
        else:
            j = i
            binseq = [ch]
            while j < ldata and len(binseq) < 8:
                ch = data[j:j+1]
                och = ord(ch)
                if och == 0 or (och > 8 and och < 0x80):
                    break
                binseq.append(ch)
                j += 1
            out.write(pack('>B', len(binseq)))
            out.write(b''.join(binseq))
            i += len(binseq) - 1
    return out.getvalue()
