# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import datetime, timezone

from vk.user import LastSeen, LastSeenField, User, UserField

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
        self.dt = dt

    @staticmethod
    def from_string(s):
        return Timestamp(datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'))

    def __str__(self):
        return self.dt.isoformat() + 'Z'

class Record(MutableMapping):
    FIELDS = (
        UserField.UID,
        UserField.FIRST_NAME,
        UserField.LAST_NAME,
        UserField.SCREEN_NAME,
        UserField.ONLINE,
        LastSeenField.TIME,
        LastSeenField.PLATFORM,
    )

    def __init__(self, timestamp=None, fields=None):
        if timestamp is None:
            timestamp = Timestamp()
        if fields is None:
            fields = OrderedDict()
        self._timestamp = timestamp
        self._fields = fields

    def __getitem__(self, field):
        if field is LastSeenField.TIME:
            return Timestamp(self._fields[field])
        return self._fields[field]

    def __setitem__(self, field, value):
        if field is LastSeenField.TIME:
            if isinstance(value, str):
                value = Timestamp.from_string(value).dt
            elif isinstance(value, Timestamp):
                value = value.dt
            elif isinstance(value, datetime):
                pass
            else:
                raise TypeError()
        if isinstance(field, LastSeenField):
            self._fields[field] = LastSeen.parse(field, value)
        elif isinstance(field, UserField):
            self._fields[field] = User.parse(field, value)
        else:
            raise TypeError()

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
        record = Record()
        for field in Record.FIELDS:
            if isinstance(field, UserField):
                record[field] = user[field]
            elif isinstance(field, LastSeenField):
                record[field] = user.get_last_seen()[field]
            else:
                assert False
        return record

    def _update_last_seen_field(self, last_seen, field):
        if field is LastSeenField.TIME:
            last_seen[field] = self[field].dt
        else:
            last_seen[field] = self[field]

    def _update_user_field(self, user, field):
        user[field] = self[field]

    def to_user(self):
        user = User()
        last_seen = LastSeen()
        for field in self:
            if isinstance(field, LastSeenField):
                self._update_last_seen_field(last_seen, field)
            elif isinstance(field, UserField):
                self._update_user_field(user, field)
            else:
                assert False
        if len(last_seen):
            user.set_last_seen(last_seen)
        return user
