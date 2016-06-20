# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import Iterable
from collections.abc import Mapping
from enum import Enum
import json
from urllib.error import URLError
import urllib.parse
from urllib.request import urlopen

import vk.error
from vk.user import User

def _split_url(url):
    return urllib.parse.urlsplit(url)[:3]

def _is_empty_param_value(value):
    return isinstance(value, str) and not value

def _filter_empty_params(params, empty_params=False):
    if empty_params:
        return params
    if isinstance(params, Mapping):
        return {name: value for name, value in params.items() if not _is_empty_param_value(value)}
    elif isinstance(params, Iterable):
        return [(name, value) for name, value in params if not _is_empty_param_value(value)]
    else:
        raise TypeError()

def _build_url(scheme, host, path, params=None, empty_params=False):
    if params is None:
        params = {}
    if isinstance(params, Mapping) or isinstance(params, Iterable):
        params = _filter_empty_params(params, empty_params)
        params = urllib.parse.urlencode(params)
    elif isinstance(params, str):
        pass
    else:
        raise TypeError()
    path = urllib.parse.quote(path)
    return urllib.parse.urlunsplit((scheme, host, path, params, ''))

def _join_param_values(values):
    if isinstance(values, str):
        return values
    elif isinstance(values, Iterable):
        return ','.join(map(str, values))
    else:
        return values

def _join_path(base, url):
    if not base.endswith('/'):
        base += '/'
    return urllib.parse.urljoin(base, url)

class Language(Enum):
    DEFAULT = None
    EN = 'en'

    def __str__(self):
        return self.value

class Method(Enum):
    USERS_GET = 'users.get'
    FRIENDS_GET = 'friends.get'

    def __str__(self):
        return self.value

class CommonParameters(Enum):
    LANGUAGE = 'lang'

    def __str__(self):
        return self.value

class API:
    _ROOT_URL = 'https://api.vk.com/method/'

    _SCHEME, _HOST, _ROOT_PATH = _split_url(_ROOT_URL)

    def __init__(self, lang=Language.DEFAULT, deactivated_users=True):
        self._common_params = {
            CommonParameters.LANGUAGE: lang,
        }
        self._skip_deactivated_users = not deactivated_users

    def _build_method_url(self, method, **params):
        path = _join_path(self._ROOT_PATH, str(method))
        params.update(self._common_params)
        return _build_url(self._SCHEME, self._HOST, path, params)

    def _call_method(self, method, **params):
        url = self._build_method_url(method, **params)
        #print(url)
        try:
            with urlopen(url) as response:
                response = json.loads(response.read().decode())
                if 'response' not in response:
                    raise vk.error.InvalidAPIResponseError(response)
                return response['response']
        except (ConnectionError, URLError):
            raise vk.error.APIConnectionError()

    def _should_skip_user(self, user):
        return self._skip_deactivated_users and user.is_deactivated()

    def _filter_response_with_users(self, user_list):
        user_list = map(User.from_api_response, user_list)
        return [user for user in user_list if not self._should_skip_user(user)]

    def users_get(self, user_ids, fields=()):
        return self._filter_response_with_users(self._call_method(
            Method.USERS_GET,
            user_ids=_join_param_values(user_ids),
            fields=_join_param_values(fields)))

    def friends_get(self, user_id, fields=()):
        return self._filter_response_with_users(self._call_method(
            Method.FRIENDS_GET,
            user_id=user_id,
            fields=_join_param_values(fields)))
