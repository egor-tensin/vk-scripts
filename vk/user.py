# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from datetime import datetime
from enum import Enum

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

    def __iter__(self):
        return iter(self._impl)

    def __getitem__(self, field):
        if isinstance(field, Field):
            field = field.value
        return self._impl[field]

    def __contains__(self, field):
        if isinstance(field, Field):
            field = field.value
        return field in self._impl

    def get_uid(self):
        return self._impl[Field.UID.value]

    def get_first_name(self):
        return self._impl[Field.FIRST_NAME.value]

    def get_last_name(self):
        return self._impl[Field.LAST_NAME.value]

    def has_last_name(self):
        return Field.LAST_NAME.value in self._impl and self.get_last_name()

    def has_screen_name(self):
        return Field.SCREEN_NAME.value in self._impl

    def get_screen_name(self):
        if self.has_screen_name():
            return self._impl[Field.SCREEN_NAME.value]
        else:
            return 'id' + str(self.get_uid())

    def is_online(self):
        return self._impl[Field.ONLINE.value]

    def get_last_seen(self):
        return datetime.fromtimestamp(self._impl[Field.LAST_SEEN.value]['time'])

    def __str__(self):
        return repr(self._impl)

    def __hash__(self):
        return hash(self.get_uid())

    def __eq__(self, other):
        return self.get_uid() == other.get_uid()
