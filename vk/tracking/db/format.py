# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from enum import Enum

from . import backend

class Format(Enum):
    CSV = 'csv'
    LOG = 'log'
    NULL = 'null'

    def create_writer(self, fd):
        if self is Format.CSV:
            return backend.csv.Writer(fd)
        elif self is Format.LOG:
            return backend.log.Writer(fd)
        elif self is Format.NULL:
            return backend.null.Writer(fd)
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def create_reader(self, fd):
        if self is Format.CSV:
            return backend.csv.Reader(fd)
        elif self is Format.LOG:
            raise NotImplementedError()
        elif self is Format.NULL:
            return backend.null.Reader(fd)
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def __str__(self):
        return self.value
