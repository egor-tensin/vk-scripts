# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from enum import Enum

from .backend import *

class Format(Enum):
    CSV = 'csv'
    LOG = 'log'
    NULL = 'null'

    def create_writer(self, fd):
        if self is Format.CSV:
            return csv.Writer(fd)
        elif self is Format.LOG:
            return log.Writer(fd)
        elif self is Format.NULL:
            return null.Writer(fd)
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def create_reader(self, fd):
        if self is Format.CSV:
            return csv.Reader(fd)
        elif self is Format.LOG:
            raise NotImplementedError()
        elif self is Format.NULL:
            return null.Reader(fd)
        else:
            raise NotImplementedError('unsupported database format: ' + str(self))

    def __str__(self):
        return self.value
