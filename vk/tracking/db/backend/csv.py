# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections.abc import Iterable
import csv

from ..record import Record
from ..timestamp import Timestamp

class Writer:
    def __init__(self, fd):
        self._fd = fd
        self._writer = csv.writer(fd, lineterminator='\n')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def on_initial_status(self, user):
        self._write_record(user)
        self._fd.flush()

    def on_status_update(self, user):
        self._write_record(user)
        self._fd.flush()

    def on_connection_error(self, e):
        pass

    def _write_record(self, user):
        if not self:
            return
        self._write_row(self._record_to_row(Record.from_user(user)))

    def _write_row(self, row):
        self._writer.writerow(row)

    @staticmethod
    def _record_to_row(record):
        return [str(record.get_timestamp())] + [str(record[field]) for field in record]

class Reader(Iterable):
    def __init__(self, fd):
        self._reader = csv.reader(fd)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __iter__(self):
        return map(Reader._record_from_row, self._reader)

    @staticmethod
    def _record_from_row(row):
        record = Record(Timestamp.from_string(row[0]))
        for i in range(len(Record.FIELDS)):
            record[Record.FIELDS[i]] = row[i + 1]
        return record
