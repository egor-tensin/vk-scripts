# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import vk.api
from vk.utils.tracking import StatusTracker
from vk.utils.tracking.db.writer import *

if __name__ == '__main__':
    import argparse, logging, sys

    def natural_number(s):
        x = int(s)
        if x < 1:
            raise argparse.ArgumentTypeError()
        return x

    parser = argparse.ArgumentParser(
        description='Track when people go online/offline.')

    parser.add_argument(metavar='UID', dest='uids', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-t', '--timeout', type=natural_number,
                        default=StatusTracker.DEFAULT_TIMEOUT,
                        help='set refresh interval (seconds)')
    parser.add_argument('-l', '--log', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='set log file path (stdout by default)')
    parser.add_argument('-o', '--output', default=None,
                        help='set status database path')

    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s] %(message)s',
                        stream=args.log,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    api = vk.api.API(vk.api.Language.EN)
    tracker = StatusTracker(api, args.timeout)

    tracker.add_initial_status_handler(log.Logger.on_initial_status)
    tracker.add_status_update_handler(log.Logger.on_status_update)
    tracker.add_connection_error_handler(log.Logger.on_exception)

    with csv.Writer(args.output) as csv_writer:

        if csv_writer:
            tracker.add_initial_status_handler(lambda user: csv_writer.write_record(user))
            tracker.add_status_update_handler(lambda user: csv_writer.write_record(user))

        try:
            tracker.loop(args.uids)
        except Exception as e:
            logging.exception(e)
            sys.exit(1)
