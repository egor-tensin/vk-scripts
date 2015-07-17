# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import api, sys

def users_get(user_ids):
    response = api.users_get(user_ids=','.join(user_ids),
                             fields='screen_name')
    if len(response) < len(user_ids):
        print('Error: couldn\'t find at least one of the users!',
              file=sys.stderr)
        sys.exit(1)
    return response

def friends_get(user_id):
    return api.friends_get(user_id=user_id)

def format_friend(user):
    s = '{} {}'.format(user['last_name'], user['first_name'])
    if 'screen_name' in user:
        s += ' ({})'.format(user['screen_name'])
    return s

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(metavar='UID', dest='user_ids', nargs='+',
                        help='user IDs or "screen names"')
    args = parser.parse_args()
    users = users_get(args.user_ids)
    user_ids = map(lambda user: user['uid'], users)
    friend_lists = map(frozenset, map(friends_get, user_ids))
    mutual_friends = frozenset.intersection(*friend_lists)
    if mutual_friends:
        mutual_friends = users_get(list(map(str, mutual_friends)))
        for friend in mutual_friends:
            print(format_friend(friend))
