# Copyright (c) 2017 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from contextlib import contextmanager
import csv
import sys

class FileWriterCSV:
    def __init__(self, fd=sys.stdout):
        self._fd = fd
        self._writer = csv.writer(fd, lineterminator='\n')

    def write_row(self, row):
        self._writer.writerow(row)
        self._fd.flush()

class FileReaderCSV:
    def __init__(self, fd=sys.stdin):
        self._reader = csv.reader(fd)

    def __iter__(self):
        return iter(self._reader)

@contextmanager
def _open_file(path=None, default=None, **kwargs):
    if path is None:
        yield default
    else:
        with open(path, **kwargs) as fd:
            yield fd

_DEFAULT_ENCODING = 'utf-8'

def open_output_text_file(path=None, mode='w'):
    return _open_file(path, default=sys.stdout, mode=mode,
                      encoding=_DEFAULT_ENCODING)

def open_input_text_file(path=None):
    return _open_file(path, default=sys.stdin, mode='r',
                      encoding=_DEFAULT_ENCODING)
