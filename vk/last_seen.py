# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import datetime, timezone
from enum import Enum
from numbers import Integral, Real

from .platform import Platform


def _parse_time(x):
    if isinstance(x, datetime):
        if x.tzinfo is None or x.tzinfo.utcoffset(x) is None:
            x = x.replace(tzinfo=timezone.utc)
        return x
    if isinstance(x, (Integral, Real)):
        return datetime.fromtimestamp(x, tz=timezone.utc)
    raise TypeError()


def _parse_platform(x):
    if isinstance(x, Platform):
        return x
    if isinstance(x, str):
        return Platform.from_string(x)
    return Platform(x)


class LastSeenField(Enum):
    TIME = 'time'
    PLATFORM = 'platform'

    def __str__(self):
        return self.value


class LastSeen(MutableMapping):
    @staticmethod
    def from_api_response(source):
        instance = LastSeen()
        for field in LastSeenField:
            if str(field) in source:
                instance[field] = source[str(field)]
        return instance

    def __init__(self, fields=None):
        if fields is None:
            fields = OrderedDict()
        self._fields = fields

    def __getitem__(self, field):
        return self._fields[field]

    def __setitem__(self, field, value):
        self._fields[field] = self.parse(field, value)

    def __delitem__(self, field):
        del self._fields[field]

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    @staticmethod
    def parse(field, value):
        if field in LastSeen._FIELD_PARSERS:
            return LastSeen._FIELD_PARSERS[field](value)
        return LastSeen._DEFAULT_FIELD_PARSER(value)

    _FIELD_PARSERS = {
        LastSeenField.TIME: _parse_time,
        LastSeenField.PLATFORM: _parse_platform,
    }

    _DEFAULT_FIELD_PARSER = str

    def has_time(self):
        return LastSeenField.TIME in self

    def get_time(self):
        return self[LastSeenField.TIME]

    def set_time(self, time):
        self[LastSeenField.TIME] = time

    def has_platform(self):
        return LastSeenField.PLATFORM in self

    def get_platform(self):
        return self[LastSeenField.PLATFORM]

    def set_platform(self, platform):
        self[LastSeenField.PLATFORM] = platform
