# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
from datetime import datetime, timezone

from vk.user import Field as UserField

def _gen_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0)

class Record:
    _USER_FIELDS = (
        UserField.UID,
        UserField.FIRST_NAME,
        UserField.LAST_NAME,
        UserField.SCREEN_NAME,
        UserField.ONLINE,
        UserField.LAST_SEEN,
    )

    def __init__(self, fields, timestamp=None):
        self._fields = fields
        self._timestamp = timestamp if timestamp is not None else _gen_timestamp()

    def __iter__(self):
        return iter(self._fields)

    def __contains__(self, field):
        return field in self._fields

    def __getitem__(self, field):
        return self._fields[field]

    def __setitem__(self, field, value):
        self._fields[field] = value

    def get_timestamp(self):
        return self._timestamp

    @staticmethod
    def _timestamp_from_string(s):
        return datetime.fromtimestamp(s)

    def timestamp_to_string(self):
        return self.get_timestamp().isoformat()

    @staticmethod
    def from_user(user):
        fields = OrderedDict()
        for field in Record._USER_FIELDS:
            fields[field] = user[field]
        if UserField.LAST_SEEN in Record._USER_FIELDS:
            fields[UserField.LAST_SEEN] = fields[UserField.LAST_SEEN].isoformat()
        return Record(fields)

    @staticmethod
    def from_row(row):
        timestamp = Record._timestamp_from_string(row[0])
        fields = OrderedDict()
        for i in range(len(Record._USER_FIELDS)):
            fields[Record._USER_FIELDS[i]] = row[i + 1]
        return Record(fields, timestamp)

    def to_row(self):
        return [self.timestamp_to_string()] + [self[field] for field in self]
