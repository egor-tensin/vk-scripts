# Copyright (c) 2016 Egor Tensin <egor@tensin.name>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import logging

from .. import meta


class Writer(meta.Writer):
    def __init__(self, fd):
        self._logger = logging.getLogger(__file__)
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(fd)
        handler.setFormatter(
            logging.Formatter(
                fmt='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S%z'
            )
        )
        self._logger.addHandler(handler)

        self._reset_last_notification()

    def info(self, *args, **kwargs):
        self._logger.info(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self._logger.exception(*args, **kwargs)

    def error(self, *args, **kwargs):
        self._logger.error(*args, **kwargs)

    def _reset_last_notification(self):
        self._last_error = False, None

    def _set_last_notification(self, e):
        self._last_error = True, str(e)

    @property
    def _last_notification_was_connection_error(self):
        return self._last_error[0]

    @property
    def _last_notification_error_message(self):
        return self._last_error[1]

    def on_initial_status(self, user):
        self._reset_last_notification()
        if user.is_online():
            self.info(self._format_user_is_online(user))
        else:
            self.info(self._format_user_is_offline(user))
        self.info(self._format_user_last_seen(user))

    def on_status_update(self, user):
        self._reset_last_notification()
        if user.is_online():
            self.info(self._format_user_went_online(user))
        else:
            self.info(self._format_user_went_offline(user))
        self.info(self._format_user_last_seen(user))

    def on_connection_error(self, e):
        if self._last_notification_was_connection_error:
            if str(e) == self._last_notification_error_message:
                self.error(self._format_another_connection_error(e))
                return
        self._set_last_notification(e)
        self.exception(e)

    @staticmethod
    def _format_user(user):
        if user.has_last_name():
            return f'{user.get_first_name()} {user.get_last_name()}'
        return f'{user.get_first_name()}'

    @staticmethod
    def _format_user_is_online(user):
        user = Writer._format_user(user)
        return f'{user} is ONLINE.'

    @staticmethod
    def _format_user_is_offline(user):
        user = Writer._format_user(user)
        return f'{user} is OFFLINE.'

    @staticmethod
    def _format_user_last_seen(user):
        last_seen = user.get_last_seen_time_local()
        platform = user.get_last_seen_platform().get_descr_text()
        user = Writer._format_user(user)
        return f'{user} was last seen at {last_seen} using {platform}.'

    @staticmethod
    def _format_user_went_online(user):
        user = Writer._format_user(user)
        return f'{user} went ONLINE.'

    @staticmethod
    def _format_user_went_offline(user):
        user = Writer._format_user(user)
        return f'{user} went OFFLINE.'

    @staticmethod
    def _format_another_connection_error(e):
        return f'Encountered a connection error which looks like the previous one: {e}'
