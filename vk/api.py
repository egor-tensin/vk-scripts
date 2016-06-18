# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import Iterable
from enum import Enum
import json
from urllib.error import URLError
import urllib.request

import vk.error
from vk.user import User

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

class API:
    def __init__(self, lang=Language.DEFAULT):
        self.lang = lang

    def _lang_is_specified(self):
        return self.lang != Language.DEFAULT

    def _format_method_params(self, **kwargs):
        params = '&'.join(map(lambda k: '{}={}'.format(k, kwargs[k]), kwargs))
        if self._lang_is_specified():
            if params:
                params += '&'
            params += 'lang={}'.format(self.lang)
        return params

    def _build_method_url(self, method, **kwargs):
        return 'https://api.vk.com/method/{}?{}'.format(
            method, self._format_method_params(**kwargs))

    def _call_method(self, method, **kwargs):
        url = self._build_method_url(method, **kwargs)
        try:
            with urllib.request.urlopen(url) as request:
                response = json.loads(request.read().decode())
                if 'response' not in response:
                    raise vk.error.InvalidAPIResponseError(response)
                return response['response']
        except (ConnectionError, URLError):
            raise vk.error.APIConnectionError()

    @staticmethod
    def _format_param_values(xs):
        if isinstance(xs, str):
            return xs
        if isinstance(xs, Iterable):
            return ','.join(map(str, xs))
        return str(xs)

    def users_get(self, user_ids, fields=()):
        return map(User.from_api_response, self._call_method(
            Method.USERS_GET,
            user_ids=self._format_param_values(user_ids),
            fields=self._format_param_values(fields)))

    def friends_get(self, user_id, fields=()):
        return map(User.from_api_response, self._call_method(
            Method.FRIENDS_GET,
            user_id=str(user_id),
            fields=self._format_param_values(fields)))
