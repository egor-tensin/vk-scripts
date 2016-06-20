# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import argparse, sys

from vk.api import API, Language
from vk.tracking import StatusTracker
from vk.tracking.db import Format as DatabaseFormat

def _parse_natural_number(s):
    x = int(s)
    if x < 1:
        raise argparse.ArgumentTypeError('must be positive: ' + x)
    return x

def _parse_output_format(s):
    try:
        return DatabaseFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid database format: ' + str(s))

def _parse_args(args=sys.argv):
    parser = argparse.ArgumentParser(
        description='Track when people go online/offline.')

    parser.add_argument('uids', metavar='UID', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-t', '--timeout', metavar='SECONDS',
                        type=_parse_natural_number,
                        default=StatusTracker.DEFAULT_TIMEOUT,
                        help='set refresh interval')
    parser.add_argument('-l', '--log', metavar='PATH', dest='log_fd',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout,
                        help='set log file path (standard output by default)')
    parser.add_argument('--output-format', dest='fmt',
                        type=_parse_output_format, default=DatabaseFormat.CSV,
                        choices=tuple(fmt for fmt in DatabaseFormat),
                        help='set database format')
    parser.add_argument('-o', '--output', metavar='PATH', dest='fd',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=None,
                        help='set database file path')

    return parser.parse_args(args[1:])

def track_status(uids, timeout=StatusTracker.DEFAULT_TIMEOUT,
                 log_fd=sys.stdout, fmt=DatabaseFormat.CSV, fd=None):

    api = API(Language.EN)
    tracker = StatusTracker(api, timeout)

    if fmt is DatabaseFormat.LOG or fd is None:
        fmt = DatabaseFormat.NULL

    with DatabaseFormat.LOG.create_writer(log_fd) as log_writer:
        tracker.add_database_writer(log_writer)
        with fmt.create_writer(fd) as db_writer:
            tracker.add_database_writer(db_writer)
            tracker.loop(uids)

def main(args=sys.argv):
    args = _parse_args(args)
    track_status(**vars(args))

if __name__ == '__main__':
    main()
