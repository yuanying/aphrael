#!/usr/bin/env python
'''
Stub qt.core module providing minimal Qt-like classes for headless operation.
Only provides enough to allow imports to succeed; actual Qt functionality is not available.
'''


class _StubClass:
    '''Generic stub that accepts any attribute access and any call.'''
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return _StubClass()
    def __call__(self, *args, **kwargs):
        return _StubClass()
    def __bool__(self):
        return False
    def __int__(self):
        return 0
    def __str__(self):
        return ''
    def __repr__(self):
        return '<StubClass>'


# SVG rasterizer stubs
QBuffer = _StubClass
QByteArray = _StubClass
QColor = _StubClass
QImage = _StubClass
QIODevice = _StubClass
QPainter = _StubClass
QSvgRenderer = _StubClass
Qt = _StubClass()
