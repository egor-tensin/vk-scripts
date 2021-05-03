# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from vk.utils.io import FileReaderCSV, FileWriterCSV

from .. import meta
from ..record import Record
from ..timestamp import Timestamp


class Writer(meta.Writer):
    def __init__(self, fd):
        self._writer = FileWriterCSV(fd, flush=True)

    def on_initial_status(self, user):
        self._write_record(user)

    def on_status_update(self, user):
        self._write_record(user)

    def on_connection_error(self, e):
        pass

    def _write_record(self, user):
        if not self:
            return
        self._writer.write_row(self._record_to_row(Record.from_user(user)))

    @staticmethod
    def _record_to_row(record):
        return [str(record.get_timestamp())] + [str(record[field]) for field in record]


class Reader(meta.Reader):
    def __init__(self, fd):
        self._reader = FileReaderCSV(fd)

    def __iter__(self):
        return map(Reader._record_from_row, self._reader)

    @staticmethod
    def _record_from_row(row):
        record = Record(Timestamp.from_string(row[0]))
        for i in range(len(Record.FIELDS)):
            record[Record.FIELDS[i]] = row[i + 1]
        return record
