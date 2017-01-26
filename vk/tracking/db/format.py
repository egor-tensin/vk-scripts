# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from contextlib import contextmanager
from enum import Enum
import sys

from . import backend

class Format(Enum):
    CSV = 'csv'
    LOG = 'log'
    NULL = 'null'

    @contextmanager
    def create_writer(self, path=None):
        with self._open_output_file(path) as fd:
            if self is Format.CSV:
                yield backend.csv.Writer(fd)
            elif self is Format.LOG:
                yield backend.log.Writer(fd)
            elif self is Format.NULL:
                yield backend.null.Writer()
            else:
                raise NotImplementedError('unsupported database format: ' + str(self))

    @contextmanager
    def _open_output_file(self, path=None):
        fd = sys.stdout
        if path is None:
            pass
        elif self is Format.CSV or self is Format.LOG:
            fd = open(path, 'w', encoding='utf-8')
        elif self is Format.NULL:
            pass
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))
        try:
            yield fd
        finally:
            if fd is not sys.stdout:
                fd.close()

    @contextmanager
    def create_reader(self, path=None):
        with self._open_input_file(path) as fd:
            if self is Format.CSV:
                yield backend.csv.Reader(fd)
            elif self is Format.LOG:
                raise NotImplementedError('cannot read from a log file')
            elif self is Format.NULL:
                yield backend.null.Reader()
            else:
                raise NotImplementedError('unsupported database format: ' + str(self))

    @contextmanager
    def _open_input_file(self, path=None):
        fd = sys.stdin
        if path is None:
            pass
        elif self is Format.CSV:
            fd = open(path, encoding='utf-8')
        elif self is Format.LOG:
            raise NotImplementedError('cannot read from a log file')
        elif self is Format.NULL:
            pass
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))
        try:
            yield fd
        finally:
            if fd is not sys.stdin:
                fd.close()

    def __str__(self):
        return self.value
