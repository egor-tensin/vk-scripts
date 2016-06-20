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

OUTPUT_FIELDS = UserField.UID, UserField.FIRST_NAME, UserField.LAST_NAME

def query_friend_list(api, user):
    return api.friends_get(user.get_uid(), fields=OUTPUT_FIELDS)

def extract_output_fields(user):
    new_user = OrderedDict()
    for field in OUTPUT_FIELDS:
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
            user = extract_output_fields(user)
            self._writer.writerow(user.values())

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd
        self._array = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._fd.write(json.dumps(self._array, indent=3, ensure_ascii=False))
        self._fd.write('\n')

    def write_mutual_friends(self, friend_list):
        for user in friend_list:
            self._array.append(extract_output_fields(user))

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

def parse_output_format(s):
    try:
        return OutputFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid output format: ' + str(s))

def parse_args(args=sys.argv):
    parser = argparse.ArgumentParser(
        description='Learn who your ex and her new boyfriend are both friends with.')

    parser.add_argument(metavar='UID', dest='uids', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('--output-format', type=parse_output_format,
                        choices=tuple(fmt for fmt in OutputFormat),
                        default=OutputFormat.CSV,
                        help='specify output format')
    parser.add_argument('--output', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout,
                        help='set output file path (standard output by default)')

    return parser.parse_args(args)

def main(args=sys.argv):
    args = parse_args(args)

    api = API(Language.EN)
    users = api.users_get(args.uids)

    friend_lists = map(lambda user: frozenset(query_friend_list(api, user)), users)
    mutual_friends = frozenset.intersection(*friend_lists)

    with args.output_format.create_writer(args.output) as writer:
        writer.write_mutual_friends(mutual_friends)

if __name__ == '__main__':
    main()
