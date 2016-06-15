# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import Callable
import csv
from datetime import datetime
import logging
import sys
import time

import vk.api
import vk.error
from vk.user import Field

class CSVWriter:
    def __init__(self, path):
        if path is None:
            self._fd = None
        else:
            self._fd = open(path, 'w')
            self._writer = csv.writer(self._fd, lineterminator='\n')

    def _is_valid(self):
        return self._fd is not None

    def __enter__(self):
        if not self._is_valid():
            return None
        self._fd.__enter__()
        return self

    def __exit__(self, *args):
        if self._is_valid():
            self._fd.__exit__(*args)

    def flush(self):
        if self._is_valid():
            self._fd.flush()

    def write_status(self, user):
        self._write_row(self._status_to_row(user))
        self.flush()

    def _write_row(self, row):
        self._writer.writerow(row)

    @staticmethod
    def _status_to_row(user):
        return [
            datetime.utcnow().replace(microsecond=0).isoformat(),
            user.get_uid(),
            user.get_first_name(),
            user.get_last_name(),
            user.get_screen_name(),
            user.is_online(),
        ]

class Logger:
    @staticmethod
    def set_up(stream=sys.stdout):
        logging.basicConfig(format='[%(asctime)s] %(message)s',
                            stream=stream,
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')

    @staticmethod
    def on_initial_status(user):
        if user.is_online():
            logging.info(Logger._format_user_is_online(user))
        else:
            logging.info(Logger._format_user_is_offline(user))
            logging.info(Logger._format_user_last_seen(user))

    @staticmethod
    def on_status_update(user):
        if user.is_online():
            logging.info(Logger._format_user_went_online(user))
        else:
            logging.info(Logger._format_user_went_offline(user))

    @staticmethod
    def on_exception(e):
        logging.exception(e)

    @staticmethod
    def _format_user(user):
        if user.has_last_name():
            return '{} {}'.format(user.get_first_name(), user.get_last_name())
        else:
            return '{}'.format(user.get_first_name())

    @staticmethod
    def _format_user_is_online(user):
        return '{} is ONLINE'.format(Logger._format_user(user))

    @staticmethod
    def _format_user_is_offline(user):
        return '{} is OFFLINE'.format(Logger._format_user(user))

    @staticmethod
    def _format_user_last_seen(user):
        return '{} was last seen at {}'.format(Logger._format_user(user), user.get_last_seen())

    @staticmethod
    def _format_user_went_online(user):
        return '{} went ONLINE'.format(Logger._format_user(user))

    @staticmethod
    def _format_user_went_offline(user):
        return '{} went OFFLINE'.format(Logger._format_user(user))

class StatusTracker:
    DEFAULT_TIMEOUT = 5

    def __init__(self, api, timeout=DEFAULT_TIMEOUT):
        self._api = api
        self._timeout = timeout
        self._on_initial_status = []
        self._on_status_update = []
        self._on_connection_error = []

    def _wait_after_connection_error(self):
        time.sleep(self._timeout)

    def add_initial_status_handler(self, fn):
        self._assert_is_callback(fn)
        self._on_initial_status.append(fn)

    def add_status_update_handler(self, fn):
        self._assert_is_callback(fn)
        self._on_status_update.append(fn)

    def add_connection_error_handler(self, fn):
        self._assert_is_callback(fn)
        self._on_connection_error.append(fn)

    @staticmethod
    def _assert_is_callback(fn):
        if not isinstance(fn, Callable):
            raise TypeError()

    USER_FIELDS = Field.SCREEN_NAME, Field.ONLINE, Field.LAST_SEEN

    def _query_status(self, uids):
        return {user.get_uid(): user for user in self._api.users_get(uids, StatusTracker.USER_FIELDS)}

    def _notify_status(self, user):
        for fn in self._on_initial_status:
            fn(user)

    def _notify_status_update(self, user):
        for fn in self._on_status_update:
            fn(user)

    def _notify_connection_error(self, e):
        for fn in self._on_connection_error:
            fn(e)

    def _query_initial_status(self, uids):
        while True:
            try:
                return self._query_status(uids)
            except vk.error.ConnectionError as e:
                self._notify_connection_error(e)
                self._wait_after_connection_error()

    def _query_status_updates(self, uids):
        while True:
            self._wait_after_connection_error()
            try:
                return self._query_status(uids)
            except vk.error.ConnectionError as e:
                self._notify_connection_error(e)

    @staticmethod
    def _filter_status_updates(old_users, new_users):
        for uid, user in new_users.items():
            if old_users[uid].is_online() != user.is_online():
                old_users[uid] = user
                yield user

    def _do_loop(self, uids):
        users = self._query_initial_status(uids)
        for user in users.values():
            self._notify_status(user)
        while True:
            updated_users = self._query_status_updates(uids)
            for user in self._filter_status_updates(users, updated_users):
                self._notify_status_update(user)

    def loop(self, uids):
        try:
            self._do_loop(uids)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    import argparse

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

    Logger.set_up(args.log)

    api = vk.api.API(vk.api.Language.EN)
    tracker = StatusTracker(api, args.timeout)

    tracker.add_initial_status_handler(Logger.on_initial_status)
    tracker.add_status_update_handler(Logger.on_status_update)
    tracker.add_connection_error_handler(Logger.on_exception)

    with CSVWriter(args.output) as csv_writer:

        if csv_writer is not None:
            tracker.add_initial_status_handler(lambda user: csv_writer.write_status(user))
            tracker.add_status_update_handler(lambda user: csv_writer.write_status(user))

        try:
            tracker.loop(args.uids)
        except Exception as e:
            Logger.on_exception(e)
            sys.exit(1)
