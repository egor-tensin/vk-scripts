# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from enum import Enum
import sys

from . import backend, io

class Format(Enum):
    CSV = 'csv'
    LOG = 'log'
    NULL = 'null'

    def __str__(self):
        return self.value

    def create_writer(self, fd=sys.stdout):
        if self is Format.CSV:
            return backend.csv.Writer(fd)
        elif self is Format.LOG:
            return backend.log.Writer(fd)
        elif self is Format.NULL:
            return backend.null.Writer()
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def open_output_file(self, path=None):
        if self is Format.CSV or self is Format.LOG:
            return io.open_output_text_file(path)
        elif self is Format.NULL:
            return io.open_output_text_file(None)
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def create_reader(self, fd=sys.stdin):
        if self is Format.CSV:
            return backend.csv.Reader(fd)
        elif self is Format.LOG:
            return NotImplementedError('cannot read from a log file')
        elif self is Format.NULL:
            return backend.null.Reader()
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def open_input_file(self, path=None):
        if self is Format.CSV:
            return io.open_input_text_file(path)
        elif self is Format.LOG:
            raise NotImplementedError('cannot read from a log file')
        elif self is Format.NULL:
            return io.open_input_text_file(None)
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))
