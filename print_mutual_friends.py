# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import api

def users_get(user_ids):
    return api.users_get(user_ids=','.join(user_ids))

def friends_get(user_id):
    return api.friends_get(user_id=user_id)

def format_user_name(user):
    return '{} {}'.format(user['last_name'], user['first_name'])

def join_user_names(user_names):
    return '{} and {}'.format(', '.join(user_names[:-1]), user_names[-1])

def print_mutual_friends(users, mutual_friends):
    user_names = list(map(format_user_name, users))
    user_names = join_user_names(user_names)
    if not mutual_friends:
        print('{} don\'t have any mutual friends'.format(user_names))
    else:
        print('{} are friends with these guys:'.format(user_names))
        for friend in mutual_friends:
            print('\t{}'.format(format_user_name(friend)))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(metavar='UID', dest='user_ids', nargs='+',
                        help='user IDs or "screen names"')
    args = parser.parse_args()
    users = users_get(args.user_ids)
    user_ids = map(lambda user: user['uid'], users)
    friend_lists = map(friends_get, user_ids)
    friend_lists = map(frozenset, friend_lists)
    mutual_friends = frozenset.intersection(*friend_lists)
    if mutual_friends:
        mutual_friends = users_get(map(str, mutual_friends))
    print_mutual_friends(users, mutual_friends)
