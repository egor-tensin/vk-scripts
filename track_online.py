# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from datetime import datetime
import time

import api

def users_get(user_ids):
    return api.users_get(user_ids=','.join(user_ids),
                         fields='online,last_seen')

def log(s):
    print('[{}] {}'.format(datetime.now().replace(microsecond=0), s))

def format_user_name(user):
    return '{} {}'.format(user['last_name'], user['first_name'])

def user_is_online(user):
    log('{} is ONLINE'.format(format_user_name(user)))

def user_is_offline(user):
    user_name = format_user_name(user)
    log('{} is OFFLINE'.format(user_name))
    last_seen = datetime.fromtimestamp(user['last_seen']['time'])
    log('{} was last seen at {}'.format(user_name, last_seen))

def user_went_online(user):
    log('{} went ONLINE'.format(format_user_name(user)))

def user_went_offline(user):
    log('{} went OFFLINE'.format(format_user_name(user)))

def print_user(status):
    if status['online']:
        user_is_online(status)
    else:
        user_is_offline(status)

def print_user_update(status):
    if status['online']:
        user_went_online(status)
    else:
        user_went_offline(status)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(metavar='UID', dest='user_ids', nargs='+',
                        help='user IDs or "screen names"')
    args = parser.parse_args()
    users = users_get(args.user_ids)
    for user in users:
        print_user(user)
    while True:
        time.sleep(5)
        updated_users = users_get(args.user_ids)
        for i in range(len(updated_users)):
            if users[i]['online'] != updated_users[i]['online']:
                users[i] = updated_users[i]
                print_user_update(updated_users[i])
