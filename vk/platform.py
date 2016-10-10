# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from enum import Enum
import re

class Platform(Enum):
    MOBILE = 1
    IPHONE = 2
    IPAD = 3
    ANDROID = 4
    WINDOWS_PHONE = 5
    WINDOWS8 = 6
    WEB = 7

    @staticmethod
    def from_string(src):
        return Platform(int(src))

    def __str__(self):
        return str(self.value)

    @staticmethod
    def _uppercase_first_letter(text):
        match = re.search(r'\w', text)
        if match is None:
            return text
        return text[:match.start()] + match.group().upper() + text[match.end():]

    def get_descr_header(self):
        return self._uppercase_first_letter(_PLATFORM_DESCRIPTIONS[self])

    def get_descr_text(self):
        descr = _PLATFORM_DESCRIPTIONS[self]
        descr = descr.replace('unrecognized', 'an unrecognized')
        return 'the ' + descr

    def get_descr_text_capitalized(self):
        return self._uppercase_first_letter(self.get_descr_text())

_PLATFORM_DESCRIPTIONS = {
    Platform.MOBILE: '"mobile" web version (or unrecognized mobile app)',
    Platform.IPHONE: 'official iPhone app',
    Platform.IPAD: 'official iPad app',
    Platform.ANDROID: 'official Android app',
    Platform.WINDOWS_PHONE: 'official Windows Phone app',
    Platform.WINDOWS8: 'official Windows 8 app',
    Platform.WEB: 'web version (or unrecognized app)'
}
