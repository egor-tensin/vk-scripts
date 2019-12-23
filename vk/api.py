# Copyright (c) 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from collections.abc import Iterable, Mapping
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
    if isinstance(params, Iterable):
        return [(name, value) for name, value in params if not _is_empty_param_value(value)]
    raise TypeError()


def _build_url(scheme, host, path, params=None, empty_params=False):
    if params is None:
        params = {}
    if isinstance(params, (Iterable, Mapping)):
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
    if isinstance(values, Iterable):
        return ','.join(map(str, values))
    return values


def _join_path(base, url):
    if not base.endswith('/'):
        base += '/'
    return urllib.parse.urljoin(base, url)


ACCESS_TOKEN = '9722cef09722cef09722cef071974b8cbe997229722cef0cbabfd816916af6c7bd37006'


class Version(Enum):
    V5_73 = '5.73'
    DEFAULT = V5_73

    def __str__(self):
        return self.value


class Language(Enum):
    EN = 'en'
    DEFAULT = EN

    def __str__(self):
        return self.value


class Method(Enum):
    USERS_GET = 'users.get'
    FRIENDS_GET = 'friends.get'

    def __str__(self):
        return self.value


class CommonParameters(Enum):
    ACCESS_TOKEN = 'access_token'
    VERSION = 'v'
    LANGUAGE = 'lang'

    def __str__(self):
        return self.value


class API:
    _ROOT_URL = 'https://api.vk.com/method/'

    _SCHEME, _HOST, _ROOT_PATH = _split_url(_ROOT_URL)

    def __init__(self, version=Version.DEFAULT, lang=Language.DEFAULT):
        self._common_params = {
            CommonParameters.ACCESS_TOKEN: ACCESS_TOKEN,
            CommonParameters.VERSION: version,
            CommonParameters.LANGUAGE: lang,
        }

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
                #print(response)
                if 'response' not in response:
                    raise vk.error.InvalidAPIResponseError(response)
                return response['response']
        except (ConnectionError, URLError) as e:
            raise vk.error.APIConnectionError(str(e)) from e

    @staticmethod
    def _filter_response_with_users(user_list, deactivated_users=True):
        user_list = map(User.from_api_response, user_list)
        if deactivated_users:
            return user_list
        return [user for user in user_list if not user.is_deactivated()]

    def users_get(self, user_ids, fields=(), deactivated_users=True):
        return self._filter_response_with_users(self._call_method(
            Method.USERS_GET,
            user_ids=_join_param_values(user_ids),
            fields=_join_param_values(fields)), deactivated_users)

    def friends_get(self, user_id, fields=(), deactivated_users=True):
        response = self._call_method(
            Method.FRIENDS_GET,
            user_id=user_id,
            fields=_join_param_values(fields))
        if 'items' not in response:
            raise vk.error.InvalidAPIResponseError(response)
        return self._filter_response_with_users(response['items'],
                                                deactivated_users)
