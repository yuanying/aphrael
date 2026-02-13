#!/usr/bin/env python
# License: GPLv3 Copyright: 2025, Kovid Goyal <kovid at kovidgoyal.net>

# Simplified atexit-based cleanup (no IPC worker)

import atexit
import os
import shutil
from contextlib import suppress
from functools import wraps
from threading import RLock

lock = RLock()


def thread_safe(f):
    @wraps(f)
    def wrapper(*a, **kw):
        with lock:
            return f(*a, **kw)
    return wrapper


def remove_dir(x):
    with suppress(Exception):
        shutil.rmtree(x, ignore_errors=True)


def unlink(path):
    with suppress(Exception):
        if os.path.exists(path):
            os.remove(path)


@thread_safe
def remove_folder_atexit(path: str) -> None:
    atexit.register(remove_dir, os.path.abspath(path))


@thread_safe
def remove_file_atexit(path: str) -> None:
    atexit.register(unlink, os.path.abspath(path))


def reset_after_fork():
    pass
