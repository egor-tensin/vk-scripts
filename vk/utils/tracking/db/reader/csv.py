# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections.abc import Iterable
import csv

from ..record import Record, Timestamp

class Reader(Iterable):
    def __init__(self, path):
        self._fd = open(path)
        self._reader = csv.reader(self._fd)

    def __enter__(self):
        self._fd.__enter__()
        return self

    def __exit__(self, *args):
        self._fd.__exit__(*args)

    def __iter__(self):
        return map(Reader._record_from_row, self._reader)

    @staticmethod
    def _record_from_row(row):
        record = Record(Timestamp.from_string(row[0]))
        for i in range(len(Record.FIELDS)):
            record[Record.FIELDS[i]] = row[i + 1]
        return record
