# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import argparse
import sys

from vk.api import API
from vk.tracking import StatusTracker
from vk.tracking.db import Format as DatabaseFormat


def _parse_args(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Show if people are online/offline.')

    parser.add_argument('uids', metavar='UID', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-l', '--log', metavar='PATH', dest='log_path',
                        help='set log file path (standard output by default)')

    return parser.parse_args(args)


def track_status(uids, log_path=None):
    api = API()
    tracker = StatusTracker(api)

    with DatabaseFormat.LOG.open_output_file(log_path) as log_fd:
        log_writer = DatabaseFormat.LOG.create_writer(log_fd)
        tracker.add_database_writer(log_writer)
        tracker.query_status(uids)


def main(args=None):
    track_status(**vars(_parse_args(args)))


if __name__ == '__main__':
    main()
