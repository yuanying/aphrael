#!/usr/bin/env python
'''
Minimal stub for calibre.gui2 - headless operation only.
'''


def must_use_qt(headless=True):
    '''Stub: No-op for headless operation.'''
    pass


def is_ok_to_use_qt():
    '''Stub: Always return True for headless operation.'''
    return True


def is_gui_thread():
    '''Stub: Always return True.'''
    return True
