# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import argparse
from collections import OrderedDict
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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def write_mutual_friends(self, friend_list):
        for user in friend_list:
            user = _filter_user_fields(user)
            self._writer.writerow(user.values())

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd
        self._arr = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._fd.write(json.dumps(self._arr, indent=3, ensure_ascii=False))
        self._fd.write('\n')

    def write_mutual_friends(self, friend_list):
        for user in friend_list:
            self._arr.append(_filter_user_fields(user))

class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'

    def __str__(self):
        return self.value

    def create_writer(self, fd=sys.stdout):
        if self is OutputFormat.CSV:
            return OutputWriterCSV(fd)
        elif self is OutputFormat.JSON:
            return OutputWriterJSON(fd)
        else:
            raise NotImplementedError('unsupported output format: ' + str(self))

def _parse_output_format(s):
    try:
        return OutputFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid output format: ' + str(s))

def _parse_args(args=sys.argv):
    parser = argparse.ArgumentParser(
        description='Learn who your ex and her new boyfriend are both friends with.')

    parser.add_argument('uids', metavar='UID', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('--output-format', dest='fmt',
                        type=_parse_output_format, default=OutputFormat.CSV,
                        choices=tuple(fmt for fmt in OutputFormat),
                        help='specify output format')
    parser.add_argument('-o', '--output', dest='fd', metavar='PATH',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout,
                        help='set output file path (standard output by default)')

    return parser.parse_args(args[1:])

def write_mutual_friends(uids, fmt=OutputFormat.CSV, fd=sys.stdout):
    api = API(Language.EN)
    users = api.users_get(uids)

    friend_lists = (frozenset(_query_friend_list(api, user)) for user in users)
    mutual_friends = frozenset.intersection(*friend_lists)

    with fmt.create_writer(fd) as writer:
        writer.write_mutual_friends(mutual_friends)

def main(args=sys.argv):
    args = _parse_args(args)
    write_mutual_friends(**vars(args))

if __name__ == '__main__':
    main()
