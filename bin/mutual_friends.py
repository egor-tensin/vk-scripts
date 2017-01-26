# Copyright (c) 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import argparse
from collections import OrderedDict
from contextlib import contextmanager
import csv
from enum import Enum
import json
import sys

from vk.api import API, Language
from vk.user import UserField

_OUTPUT_USER_FIELDS = UserField.UID, UserField.FIRST_NAME, UserField.LAST_NAME

def _query_friend_list(api, user):
    return api.friends_get(user.get_uid(), fields=_OUTPUT_USER_FIELDS)

def _filter_user_fields(user):
    new_user = OrderedDict()
    for field in _OUTPUT_USER_FIELDS:
        new_user[str(field)] = user[field] if field in user else None
    return new_user

class OutputWriterCSV:
    def __init__(self, fd=sys.stdout):
        self._writer = csv.writer(fd, lineterminator='\n')

    def write_mutual_friends(self, friend_list):
        for user in friend_list:
            user = _filter_user_fields(user)
            self._writer.writerow(user.values())

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd

    def write_mutual_friends(self, friend_list):
        arr = []
        for user in friend_list:
            arr.append(_filter_user_fields(user))
        self._fd.write(json.dumps(arr, indent=3, ensure_ascii=False))
        self._fd.write('\n')

class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'

    def __str__(self):
        return self.value

    @contextmanager
    def create_writer(self, path=None):
        with self._open_file(path) as fd:
            if self is OutputFormat.CSV:
                yield OutputWriterCSV(fd)
            elif self is OutputFormat.JSON:
                yield OutputWriterJSON(fd)
            else:
                raise NotImplementedError('unsupported output format: ' + str(self))

    @staticmethod
    @contextmanager
    def _open_file(path=None):
        fd = sys.stdout
        if path is None:
            pass
        else:
            fd = open(path, 'w', encoding='utf-8')
        try:
            yield fd
        finally:
            if fd is not sys.stdout:
                fd.close()

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
    api = API(Language.EN)
    users = api.users_get(uids)

    friend_lists = (frozenset(_query_friend_list(api, user)) for user in users)
    mutual_friends = frozenset.intersection(*friend_lists)

    with out_fmt.create_writer(out_path) as writer:
        writer.write_mutual_friends(mutual_friends)

def main(args=None):
    write_mutual_friends(**vars(_parse_args(args)))

if __name__ == '__main__':
    main()
