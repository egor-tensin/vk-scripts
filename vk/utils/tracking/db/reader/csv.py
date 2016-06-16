# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import csv

from ..record import Record

class Reader:
    def __init__(self, path):
        self._fd = open(path)
        self._reader = csv.reader(self._fd)

    def __enter__(self):
        self._fd.__enter__()
        return self

    def __exit__(self, *args):
        self._fd.__exit__(*args)

    def __iter__(self):
        return map(Record.from_row, self._reader)
