# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
import csv
from enum import Enum
import json
import sys

import vk.api
from vk.user import UserField

OUTPUT_FIELDS = UserField.UID, UserField.FIRST_NAME, UserField.LAST_NAME, UserField.SCREEN_NAME

def query_friend_list(api, user):
    return api.friends_get(user.get_uid(), fields=OUTPUT_FIELDS)

def extract_output_fields(user):
    new_user = OrderedDict()
    for field in OUTPUT_FIELDS:
        new_user[str(field)] = user[field] if field in user else None
    return new_user

def print_mutual_friends_csv(mutual_friends):
    writer = csv.writer(sys.stdout, lineterminator='\n')
    for user in mutual_friends:
        user = extract_output_fields(user)
        writer.writerow(user.values())

def print_mutual_friends_json(mutual_friends):
    print(json.dumps([extract_output_fields(user) for user in mutual_friends], indent=3))

def print_mutual_friends(mutual_friends, output_format):
    if output_format is OutputFormat.CSV:
        print_mutual_friends_csv(mutual_friends)
    elif output_format is OutputFormat.JSON:
        print_mutual_friends_json(mutual_friends)
    else:
        raise NotImplementedError('unsupported output format: ' + str(output_format))

class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'

    def __str__(self):
        return self.value

if __name__ == '__main__':
    import argparse

    def output_format(s):
        try:
            return OutputFormat(s)
        except ValueError:
            raise argparse.ArgumentError()

    parser = argparse.ArgumentParser(
        description='Learn who your ex and her new boyfriend are both friends with.')

    parser.add_argument(metavar='UID', dest='uids', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-f', '--format', type=output_format,
                        choices=tuple(x for x in OutputFormat),
                        default=OutputFormat.CSV,
                        help='specify output format')
    args = parser.parse_args()

    api = vk.api.API(vk.api.Language.EN)
    users = api.users_get(args.uids)

    friend_lists = map(lambda user: frozenset(query_friend_list(api, user)), users)
    mutual_friends = frozenset.intersection(*friend_lists)
    print_mutual_friends(mutual_friends, args.format)
