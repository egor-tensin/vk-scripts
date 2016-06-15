# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
from datetime import datetime

from vk.user import Field

class Record:
    _FIELDS = (
        Field.UID,
        Field.FIRST_NAME,
        Field.LAST_NAME,
        Field.SCREEN_NAME,
        Field.ONLINE,
        Field.LAST_SEEN,
    )

    def __init__(self, user):
        self._fields = OrderedDict()
        for field in self._FIELDS:
            self._fields[field] = user[field]
        self._timestamp = datetime.utcnow().replace(microsecond=0)

    def to_list(self):
        return [self._timestamp.isoformat()] + list(self._fields.values())
