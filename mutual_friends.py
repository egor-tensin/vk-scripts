# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import vk.api
import vk.user

def query_friends(api, user):
    return api.friends_get(user.get_uid(), fields=vk.user.Field.SCREEN_NAME)

def format_user(user):
    if user.has_last_name():
        return '{} {} ({})'.format(user.get_last_name(), user.get_first_name(), user.get_screen_name())
    else:
        return '{} ({})'.format(user.get_first_name(), user.get_screen_name())

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Learn who your ex and her new boyfriend are both friends with.')

    parser.add_argument(metavar='UID', dest='uids', nargs='+',
                        help='user IDs or "screen names"')
    args = parser.parse_args()

    api = vk.api.API(vk.api.Language.EN)
    users = api.users_get(args.uids, fields=vk.user.Field.SCREEN_NAME)

    friend_lists = map(lambda user: frozenset(query_friends(api, user)), users)
    mutual_friends = frozenset.intersection(*friend_lists)
    if mutual_friends:
        for friend in mutual_friends:
            print(format_user(friend))
