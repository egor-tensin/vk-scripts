# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import csv
from datetime import datetime

from ..record import Record

class Writer:
    def __init__(self, path, mode='w'):
        if path is None:
            self._fd = None
        else:
            self._fd = open(path, mode)
            self._writer = csv.writer(self._fd, lineterminator='\n')

    def _is_valid(self):
        return self._fd is not None

    def __enter__(self):
        if not self._is_valid():
            return None
        self._fd.__enter__()
        return self

    def __exit__(self, *args):
        if self._is_valid():
            self._fd.__exit__(*args)

    def flush(self):
        if self._is_valid():
            self._fd.flush()

    def write_record(self, user):
        self._write_row(Record(user).to_list())
        self.flush()

    def _write_row(self, row):
        self._writer.writerow(row)
