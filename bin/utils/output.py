# Copyright (c) 2017 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from contextlib import contextmanager
import csv
import json
import sys

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd

    def write(self, something):
        self._fd.write(json.dumps(something, indent=3, ensure_ascii=False))
        self._fd.write('\n')

class OutputWriterCSV:
    def __init__(self, fd=sys.stdout):
        self._writer = csv.writer(fd, lineterminator='\n')

    def write_row(self, row):
        self._writer.writerow(row)

@contextmanager
def _open_file(path=None, **kwargs):
    fd = sys.stdout
    if path is None:
        pass
    else:
        fd = open(path, **kwargs)
    try:
        yield fd
    finally:
        if fd is not sys.stdout:
            fd.close()

def open_text_file(path=None):
    return _open_file(path, mode='w', encoding='utf-8')

def open_binary_file(path=None):
    return _open_file(path, mode='wb')
