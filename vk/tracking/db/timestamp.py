# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from datetime import datetime, timezone

class Timestamp:
    @staticmethod
    def _new():
        return datetime.utcnow()

    @staticmethod
    def _is_timezone_aware(impl):
        return impl.tzinfo is not None and impl.tzinfo.utcoffset(impl) is not None

    @staticmethod
    def _lose_timezone(impl):
        if Timestamp._is_timezone_aware(impl):
            return impl.astimezone(timezone.utc).replace(tzinfo=None)
        return impl

    def __init__(self, impl=None):
        if impl is None:
            impl = self._new()
        impl = impl.replace(microsecond=0)
        impl = self._lose_timezone(impl)
        self.impl = impl

    @staticmethod
    def from_string(src):
        return Timestamp(datetime.strptime(src, '%Y-%m-%dT%H:%M:%SZ'))

    def __str__(self):
        return self.impl.isoformat() + 'Z'
