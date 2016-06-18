# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

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
    def from_string(s):
        return Platform(int(s))

    def __str__(self):
        return str(self.value)

    @staticmethod
    def _uppercase_first_letter(s):
        m = re.search(r'\w', s)
        if m is None:
            return s
        return s[:m.start()] + m.group().upper() + s[m.end():]

    def get_descr_header(self):
        return self._uppercase_first_letter(_PLATFORM_DESCRIPTIONS[self])

    def get_descr_text(self):
        s = _PLATFORM_DESCRIPTIONS[self]
        s = s.replace('unrecognized', 'an unrecognized')
        return 'the ' + s

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
