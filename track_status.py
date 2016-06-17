# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from vk.api import API, Language
from vk.utils.tracking import StatusTracker
from vk.utils.tracking.db import Format

if __name__ == '__main__':
    import argparse, sys

    def natural_number(s):
        x = int(s)
        if x < 1:
            raise argparse.ArgumentTypeError()
        return x

    def output_format(s):
        try:
            return Format(s)
        except ValueError:
            raise argparse.ArgumentTypeError()

    parser = argparse.ArgumentParser(
        description='Track when people go online/offline.')

    parser.add_argument(metavar='UID', dest='uids', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-t', '--timeout', type=natural_number,
                        default=StatusTracker.DEFAULT_TIMEOUT,
                        help='set refresh interval (seconds)')
    parser.add_argument('-l', '--log', default=sys.stdout,
                        type=argparse.FileType('w'),
                        help='set log file path (standard output by default)')
    parser.add_argument('--output-format',
                        type=output_format, default=Format.CSV,
                        choices=tuple(fmt for fmt in Format),
                        help='set database format')
    parser.add_argument('-o', '--output', default=None,
                        type=argparse.FileType('w'),
                        help='set database file path')

    args = parser.parse_args()

    api = API(Language.EN)
    tracker = StatusTracker(api, args.timeout)

    if args.output_format is Format.LOG or args.output is None:
        args.output_format = Format.NULL

    with Format.LOG.create_writer(args.log) as log_writer:
        tracker.add_database_writer(log_writer)
        with args.output_format.create_writer(args.output) as db_writer:
            tracker.add_database_writer(db_writer)
            try:
                tracker.loop(args.uids)
            except Exception as e:
                log_writer.exception(e)
                sys.exit(1)
