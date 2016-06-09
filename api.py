# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import collections
from datetime import datetime
from enum import Enum
import json
import sys
from urllib.error import URLError
import urllib.request

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

class User:
    def __init__(self, impl):
        self._impl = impl

    def get_uid(self):
        return self._impl[self.Field.UID.value]

    def get_first_name(self):
        return self._impl[self.Field.FIRST_NAME.value]

    def get_last_name(self):
        return self._impl[self.Field.LAST_NAME.value]

    def has_last_name(self):
        return self.Field.LAST_NAME.value in self._impl and self.get_last_name()

    def has_screen_name(self):
        return self.Field.SCREEN_NAME.value in self._impl

    def get_screen_name(self):
        if self.has_screen_name():
            return self._impl[self.Field.SCREEN_NAME.value]
        else:
            return 'id' + str(self.get_uid())

    def is_online(self):
        return self._impl[self.Field.ONLINE.value]

    def get_last_seen(self):
        return datetime.fromtimestamp(self._impl[self.Field.LAST_SEEN.value]['time'])

    def __str__(self):
        return repr(self._impl)

    def __hash__(self):
        return hash(self.get_uid())

    def __eq__(self, other):
        return self.get_uid() == other.get_uid()

    class Field(Enum):
        UID = 'uid'
        FIRST_NAME = 'first_name'
        LAST_NAME = 'last_name'
        SCREEN_NAME = 'screen_name'
        ONLINE = 'online'
        LAST_SEEN = 'last_seen'

        def __str__(self):
            return self.value


class Error(RuntimeError):
    pass

class InvalidResponseError(Error):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return str(self.response)

class ConnectionError(Error):
    pass

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
                    raise InvalidResponseError(response)
                return response['response']
        except URLError:
            raise ConnectionError()

    @staticmethod
    def _format_param_values(xs):
        if isinstance(xs, str):
            return xs
        if isinstance(xs, collections.Iterable):
            return ','.join(map(str, xs))
        return str(xs)

    def users_get(self, user_ids, fields=()):
        return map(User, self._call_method(
            Method.USERS_GET,
            user_ids=self._format_param_values(user_ids),
            fields=self._format_param_values(fields)))

    def friends_get(self, user_id, fields=()):
        return map(User, self._call_method(
            Method.FRIENDS_GET,
            user_id=str(user_id),
            fields=self._format_param_values(fields)))
