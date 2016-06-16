# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from datetime import datetime, timezone
from enum import Enum
from numbers import Real, Integral

class Field(Enum):
    UID = 'uid'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    SCREEN_NAME = 'screen_name'
    ONLINE = 'online'
    LAST_SEEN = 'last_seen'

    def __str__(self):
        return self.value

class User:
    def __init__(self, impl):
        self._impl = impl

    def __str__(self):
        return str(self._impl)

    def __eq__(self, other):
        return self.get_uid() == other.get_uid()

    def __hash__(self):
        return hash(self.get_uid())

    def __iter__(self):
        return iter(self._impl)

    def __contains__(self, field):
        if field is Field.LAST_SEEN:
            return self._has_last_seen()
        return self._normalize_field(field) in self._impl

    def __getitem__(self, field):
        if field is Field.LAST_SEEN:
            return self._get_last_seen()
        return self._impl[self._normalize_field(field)]

    def __setitem__(self, field, value):
        if field is Field.LAST_SEEN:
            self._set_last_seen(value)
        else:
            self._impl[self._normalize_field(field)] = value

    @staticmethod
    def _normalize_field(field):
        if isinstance(field, Field):
            return field.value
        return field

    def get_uid(self):
        return self[Field.UID]

    def get_first_name(self):
        return self[Field.FIRST_NAME]

    def set_first_name(self, name):
        self[Field.FIRST_NAME] = name

    def has_last_name(self):
        return Field.LAST_NAME in self and self.get_last_name()

    def get_last_name(self):
        return self[Field.LAST_NAME]

    def set_last_name(self, name):
        self[Field.LAST_NAME] = name

    def has_screen_name(self):
        return Field.SCREEN_NAME in self

    def get_screen_name(self):
        if self.has_screen_name():
            return self[Field.SCREEN_NAME]
        else:
            return 'id' + str(self.get_uid())

    def set_screen_name(self, name):
        self[Field.SCREEN_NAME] = name

    def has_online(self):
        return Field.ONLINE in self

    def is_online(self):
        return bool(self[Field.ONLINE])

    def set_online(self, value=True):
        self[Field.ONLINE] = value

    @staticmethod
    def _last_seen_from_timestamp(t):
        return datetime.fromtimestamp(t, timezone.utc)

    @staticmethod
    def _last_seen_to_timestamp(t):
        if isinstance(t, datetime):
            return t.timestamp()
        elif isinstance(t, Real) or isinstance(t, Integral):
            return t
        else:
            raise TypeError('"last seen" time must be either a `datetime` or a POSIX timestamp')

    def _has_last_seen(self):
        return Field.LAST_SEEN.value in self._impl and 'time' in self._impl[Field.LAST_SEEN.value]

    def has_last_seen(self):
        return self._has_last_seen()

    def _get_last_seen(self):
        return self._last_seen_from_timestamp(self._impl[Field.LAST_SEEN.value]['time'])

    def get_last_seen_utc(self):
        return self._get_last_seen()

    def get_last_seen_local(self):
        return self._get_last_seen().astimezone()

    def _set_last_seen(self, t):
        if Field.LAST_SEEN.value not in self._impl:
            self._impl[Field.LAST_SEEN.value] = {}
        self._impl[Field.LAST_SEEN.value]['time'] = self._last_seen_to_timestamp(t)

    def set_last_seen(self, t):
        self._set_last_seen(t)
