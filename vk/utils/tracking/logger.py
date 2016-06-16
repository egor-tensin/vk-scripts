# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import logging
import sys

class Logger:
    @staticmethod
    def set_up(fd=sys.stdout):
        logging.basicConfig(format='[%(asctime)s] %(message)s',
                            stream=fd,
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
        logging.info(Logger._format_user_last_seen(user))

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
        return '{} was last seen at {}'.format(Logger._format_user(user), user.get_last_seen_time_local())

    @staticmethod
    def _format_user_went_online(user):
        return '{} went ONLINE'.format(Logger._format_user(user))

    @staticmethod
    def _format_user_went_offline(user):
        return '{} went OFFLINE'.format(Logger._format_user(user))
