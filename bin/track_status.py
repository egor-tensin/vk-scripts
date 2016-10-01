# Copyright (c) 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import argparse, sys

from vk.api import API, Language
from vk.tracking import StatusTracker
from vk.tracking.db import Format as DatabaseFormat

DEFAULT_TIMEOUT = StatusTracker.DEFAULT_TIMEOUT
DEFAULT_DB_FORMAT = DatabaseFormat.CSV

def _parse_positive_integer(s):
    try:
        x = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError('must be a positive integer: ' + s)
    if x < 1:
        raise argparse.ArgumentTypeError('must be a positive integer: ' + s)
    return x

def _parse_database_format(s):
    try:
        return DatabaseFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid database format: ' + s)

def _parse_args(args=sys.argv):
    parser = argparse.ArgumentParser(
        description='Track when people go online/offline.')

    parser.add_argument('uids', metavar='UID', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-t', '--timeout', metavar='SECONDS',
                        type=_parse_positive_integer,
                        default=DEFAULT_TIMEOUT,
                        help='set refresh interval')
    parser.add_argument('-l', '--log', metavar='PATH', dest='log_fd',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout,
                        help='set log file path (standard output by default)')
    parser.add_argument('-f', '--format', dest='db_fmt',
                        type=_parse_database_format,
                        choices=DatabaseFormat,
                        default=DEFAULT_DB_FORMAT,
                        help='specify database format')
    parser.add_argument('-o', '--output', metavar='PATH', dest='db_fd',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=None,
                        help='set database file path')

    return parser.parse_args(args[1:])

def track_status(
        uids, timeout=DEFAULT_TIMEOUT,
        log_fd=sys.stdout,
        db_fd=None, db_fmt=DEFAULT_DB_FORMAT):

    api = API(Language.EN, deactivated_users=False)
    tracker = StatusTracker(api, timeout)

    if db_fmt is DatabaseFormat.LOG or db_fd is None:
        db_fmt = DatabaseFormat.NULL

    with DatabaseFormat.LOG.create_writer(log_fd) as log_writer:
        tracker.add_database_writer(log_writer)
        with db_fmt.create_writer(db_fd) as db_writer:
            tracker.add_database_writer(db_writer)
            tracker.loop(uids)

def main(args=sys.argv):
    args = _parse_args(args)
    track_status(**vars(args))

if __name__ == '__main__':
    main()
