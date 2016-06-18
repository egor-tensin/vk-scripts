# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from datetime import datetime, timezone

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
