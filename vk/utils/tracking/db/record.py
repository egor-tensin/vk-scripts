# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import datetime, timezone

from vk.user import LastSeen, User, UserField

class Timestamp:
    @staticmethod
    def _new():
        return datetime.utcnow()

    @staticmethod
    def _is_timezone_aware(dt):
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

    @staticmethod
    def _lose_timezone(dt):
        if Timestamp._is_timezone_aware(dt):
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    def __init__(self, dt=None):
        if dt is None:
            dt = self._new()
        dt = dt.replace(microsecond=0)
        dt = self._lose_timezone(dt)
        self._dt = dt

    @staticmethod
    def from_string(s):
        return Timestamp(datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'))

    def __str__(self):
        return self._dt.isoformat() + 'Z'

    @staticmethod
    def from_last_seen(ls):
        return Timestamp(ls.get_time())

    def to_last_seen(self):
        ls = LastSeen()
        ls.set_time(self._dt)
        return ls

class Record(MutableMapping):
    FIELDS = (
        UserField.UID,
        UserField.FIRST_NAME,
        UserField.LAST_NAME,
        UserField.SCREEN_NAME,
        UserField.ONLINE,
        UserField.LAST_SEEN,
    )

    def __init__(self, timestamp=None, fields=None):
        if timestamp is None:
            timestamp = Timestamp()
        if fields is None:
            fields = OrderedDict()
        self._timestamp = timestamp
        self._fields = fields

    def __getitem__(self, field):
        if field is UserField.LAST_SEEN:
            return Timestamp.from_last_seen(self._fields[field])
        return self._fields[field]

    def __setitem__(self, field, value):
        if field is UserField.LAST_SEEN:
            if isinstance(value, str):
                value = Timestamp.from_string(value).to_last_seen()
            elif isinstance(value, Timestamp):
                value = value.to_last_seen()
            elif isinstance(value, LastSeen):
                pass
            else:
                raise TypeError()
        self._fields[field] = User.parse(field, value)

    def __delitem__(self, field):
        del self._fields[field]

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    def get_timestamp(self):
        return self._timestamp

    @staticmethod
    def from_user(user):
        instance = Record()
        for field in Record.FIELDS:
            instance[field] = user[field]
        return instance

    def to_user(self):
        user = User()
        for field in self:
            user[field] = self[field]
        return user
