# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections.abc import Iterable

class Writer:
    def __init__(self, fd):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def on_initial_status(self, user):
        pass

    def on_status_update(self, user):
        pass

    def on_connection_error(self, e):
        pass

class Reader(Iterable):
    def __init__(self, fd):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __iter__(self):
        pass
