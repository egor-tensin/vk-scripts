# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import logging

class Writer:
    def __init__(self, fd):
        self._logger = logging.getLogger(__file__)
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(fd)
        handler.setFormatter(logging.Formatter(
            fmt='[%(asctime)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))
        self._logger.addHandler(handler)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def info(self, msg):
        self._logger.info(msg)

    def exception(self, e):
        self._logger.exception(e)

    def on_initial_status(self, user):
        if user.is_online():
            self.info(self._format_user_is_online(user))
        else:
            self.info(self._format_user_is_offline(user))
        self.info(self._format_user_last_seen(user))

    def on_status_update(self, user):
        if user.is_online():
            self.info(self._format_user_went_online(user))
        else:
            self.info(self._format_user_went_offline(user))
        self.info(self._format_user_last_seen(user))

    def on_connection_error(self, e):
        #self.exception(e)
        pass

    @staticmethod
    def _format_user(user):
        if user.has_last_name():
            return '{} {}'.format(user.get_first_name(), user.get_last_name())
        else:
            return '{}'.format(user.get_first_name())

    @staticmethod
    def _format_user_is_online(user):
        return '{} is ONLINE.'.format(Writer._format_user(user))

    @staticmethod
    def _format_user_is_offline(user):
        return '{} is OFFLINE.'.format(Writer._format_user(user))

    @staticmethod
    def _format_user_last_seen(user):
        return '{} was last seen at {} using {}.'.format(
            Writer._format_user(user),
            user.get_last_seen_time_local(),
            user.get_last_seen_platform().get_descr_text())

    @staticmethod
    def _format_user_went_online(user):
        return '{} went ONLINE.'.format(Writer._format_user(user))

    @staticmethod
    def _format_user_went_offline(user):
        return '{} went OFFLINE.'.format(Writer._format_user(user))
