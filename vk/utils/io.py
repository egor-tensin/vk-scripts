# Copyright (c) 2017 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from contextlib import contextmanager
import csv
import json
import sys


class FileWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd

    def write(self, something):
        self._fd.write(json.dumps(something, indent=3, ensure_ascii=False))
        self._fd.write('\n')


class FileReaderCSV:
    def __init__(self, fd=sys.stdin):
        self._reader = csv.reader(fd)

    def __iter__(self):
        return iter(self._reader)


class FileWriterCSV:
    def __init__(self, fd=sys.stdout, flush=False):
        self._fd = fd
        self._writer = csv.writer(fd, lineterminator='\n')
        self._flush = flush

    @staticmethod
    def _convert_row_old_python(row):
        if isinstance(row, (list, tuple)):
            return row
        return list(row)

    def write_row(self, row):
        if sys.version_info < (3, 5):
            row = self._convert_row_old_python(row)
        self._writer.writerow(row)
        if self._flush:
            self._fd.flush()


@contextmanager
def _open_file(path=None, default=None, **kwargs):
    if path is None:
        yield default
    else:
        with open(path, **kwargs) as fd:
            yield fd


_DEFAULT_ENCODING = 'utf-8'


def open_input_text_file(path=None):
    return _open_file(path, default=sys.stdin, mode='r',
                      encoding=_DEFAULT_ENCODING)


def open_output_text_file(path=None, mode='w'):
    return _open_file(path, default=sys.stdout, mode=mode,
                      encoding=_DEFAULT_ENCODING)


def open_output_binary_file(path=None):
    return _open_file(path, default=sys.stdout, mode='wb')
