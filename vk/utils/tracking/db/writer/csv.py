# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import csv

from ..record import Record

class Writer:
    def __init__(self, path, mode='w'):
        if path is None:
            self._fd = None
        else:
            self._fd = open(path, mode)
            self._writer = csv.writer(self._fd, lineterminator='\n')

    def __bool__(self):
        return self._fd is not None

    def __enter__(self):
        if not self:
            return self
        self._fd.__enter__()
        return self

    def __exit__(self, *args):
        if not self:
            return
        self._fd.__exit__(*args)

    def flush(self):
        if not self:
            return
        self._fd.flush()

    def write_record(self, user):
        if not self:
            return
        self._write_row(Record.from_user(user).to_row())
        self.flush()

    def _write_row(self, row):
        self._writer.writerow(row)
