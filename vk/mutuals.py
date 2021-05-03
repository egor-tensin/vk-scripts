# Copyright (c) 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import abc
import argparse
from collections import OrderedDict
from enum import Enum
import sys

from vk.api import API
from vk.user import UserField
from vk.utils import io


_OUTPUT_USER_FIELDS = UserField.UID, UserField.FIRST_NAME, UserField.LAST_NAME


def _query_friend_list(api, user):
    return api.friends_get(user.get_uid(), fields=_OUTPUT_USER_FIELDS)


def _filter_user_fields(user):
    new_user = OrderedDict()
    for field in _OUTPUT_USER_FIELDS:
        new_user[str(field)] = user[field] if field in user else None
    return new_user


class OutputSinkMutualFriends(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write_mutual_friends(self, friend_list):
        pass


class OutputSinkCSV(OutputSinkMutualFriends):
    def __init__(self, fd=sys.stdout):
        self._writer = io.FileWriterCSV(fd)

    def write_mutual_friends(self, friend_list):
        for user in friend_list:
            self._writer.write_row(user.values())


class OutputSinkJSON(OutputSinkMutualFriends):
    def __init__(self, fd=sys.stdout):
        self._writer = io.FileWriterJSON(fd)

    def write_mutual_friends(self, friend_list):
        self._writer.write(friend_list)


class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'

    def __str__(self):
        return self.value

    @staticmethod
    def open_file(path=None):
        return io.open_output_text_file(path)

    def create_sink(self, fd=sys.stdout):
        if self is OutputFormat.CSV:
            return OutputSinkCSV(fd)
        if self is OutputFormat.JSON:
            return OutputSinkJSON(fd)
        raise NotImplementedError('unsupported output format: ' + str(self))


def _parse_output_format(s):
    try:
        return OutputFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid output format: ' + s)


def _parse_args(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Learn who your ex and her new boyfriend are both friends with.')

    parser.add_argument('uids', metavar='UID', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-f', '--format', dest='out_fmt',
                        type=_parse_output_format,
                        default=OutputFormat.CSV,
                        choices=OutputFormat,
                        help='specify output format')
    parser.add_argument('-o', '--output', metavar='PATH', dest='out_path',
                        help='set output file path (standard output by default)')

    return parser.parse_args(args)


def write_mutual_friends(uids, out_path=None, out_fmt=OutputFormat.CSV):
    api = API()
    users = api.users_get(uids)

    friend_lists = (frozenset(_query_friend_list(api, user)) for user in users)
    mutual_friends = frozenset.intersection(*friend_lists)
    mutual_friends = [_filter_user_fields(user) for user in mutual_friends]

    with out_fmt.open_file(out_path) as out_fd:
        sink = out_fmt.create_sink(out_fd)
        sink.write_mutual_friends(mutual_friends)


def main(args=None):
    write_mutual_friends(**vars(_parse_args(args)))


if __name__ == '__main__':
    main()
