# Copyright (c) 2016 Egor Tensin <egor@tensin.name>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from enum import Enum


class Platform(Enum):
    # https://dev.vk.com/en/reference/objects/user#last_seen
    MOBILE = 1
    IPHONE = 2
    IPAD = 3
    ANDROID = 4
    WINDOWS_PHONE = 5
    WINDOWS10 = 6
    WEB = 7

    @staticmethod
    def from_string(s):
        return Platform(int(s))

    def __str__(self):
        return str(self.value)

    @property
    def descr(self):
        return f'the {_PLATFORM_DESCRIPTIONS[self]}'


_PLATFORM_DESCRIPTIONS = {
    Platform.MOBILE: '"mobile" web version (or an unrecognized mobile app)',
    Platform.IPHONE: 'official iPhone app',
    Platform.IPAD: 'official iPad app',
    Platform.ANDROID: 'official Android app',
    Platform.WINDOWS_PHONE: 'official Windows Phone app',
    Platform.WINDOWS10: 'official Windows 10 app',
    Platform.WEB: 'web version (or an unrecognized app)',
}
