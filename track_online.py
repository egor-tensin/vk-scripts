# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import argparse
from datetime import datetime
import logging
import time
import sys

import api

def users_get(user_ids):
    response = api.users_get(user_ids=','.join(user_ids),
                             fields='online,last_seen')
    if len(response) < len(user_ids):
        raise RuntimeError('Couldn\'t update status of at least one of the users!')
    return response

def format_user_name(user):
    return '{} {}'.format(user['last_name'], user['first_name'])

def user_is_online(user):
    logging.info('{} is ONLINE'.format(format_user_name(user)))

def user_is_offline(user):
    user_name = format_user_name(user)
    logging.info('{} is OFFLINE'.format(user_name))
    last_seen = datetime.fromtimestamp(user['last_seen']['time'])
    logging.info('{} was last seen at {}'.format(user_name, last_seen))

def user_went_online(user):
    logging.info('{} went ONLINE'.format(format_user_name(user)))

def user_went_offline(user):
    logging.info('{} went OFFLINE'.format(format_user_name(user)))

def print_user(status):
    if status['online']:
        user_is_online(status)
    else:
        user_is_offline(status)

def print_status_update(status):
    if status['online']:
        user_went_online(status)
    else:
        user_went_offline(status)

def parse_timeout(source):
    timeout = int(source)
    if timeout < 1:
        raise argparse.ArgumentTypeError(
            'please specify a positive number of seconds as refresh timeout')
    return timeout

DEFAULT_TIMEOUT=5

def print_initial_status(user_ids):
    users = users_get(user_ids)
    for user in users:
        print_user(user)
    return users

def loop_update_status(users, user_ids, timeout=DEFAULT_TIMEOUT):
    while True:
        time.sleep(timeout)
        updated_users = users_get(user_ids)
        for i in range(len(updated_users)):
            if users[i]['online'] != updated_users[i]['online']:
                users[i] = updated_users[i]
                print_status_update(updated_users[i])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Track when people go online/offline.')
    parser.add_argument(metavar='UID', dest='user_ids', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-t', '--timeout', default=DEFAULT_TIMEOUT,
                        type=parse_timeout,
                        help='set refresh interval (seconds)')
    parser.add_argument('-l', '--log', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='set log file path (stdout by default)')
    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s] %(message)s',
                        stream=args.log,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    try:
        users = print_initial_status(args.user_ids)
        loop_update_status(users, args.user_ids, timeout=args.timeout)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
