# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import json, sys, urllib.request

def call_method(method_name, **kwargs):
    get_args = '&'.join(map(lambda k: '{}={}'.format(k, kwargs[k]), kwargs))
    url = 'https://api.vk.com/method/{}?{}'.format(method_name, get_args)
    response = json.loads(urllib.request.urlopen(url).read().decode())
    if 'response' not in response:
        print(response, file=sys.stderr)
        sys.exit(-1)
    return response['response']

def users_get(**kwargs):
    return call_method('users.get', **kwargs)

def friends_get(**kwargs):
    return call_method('friends.get', **kwargs)
