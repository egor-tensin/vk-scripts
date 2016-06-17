# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections.abc import MutableMapping

from vk.user import User

class OnlinePeriodEnumerator(MutableMapping):
    def __init__(self):
        self._records_by_user = {}

    def __getitem__(self, key):
        return self._records_by_user[self._normalize_key(key)]

    def __setitem__(self, key, value):
        self._records_by_user[self._normalize_key(key)] = value

    def __delitem__(self, key):
        del self._records_by_user[self._normalize_key(key)]

    def __iter__(self):
        return iter(self._records_by_user)

    def __len__(self):
        return len(self._records_by_user)

    @staticmethod
    def _normalize_key(key):
        return key.get_uid() if isinstance(key, User) else key

    def enum(self, db_reader):
        for record in db_reader:
            period = self._insert_record(record)
            #print(period)
            if period is not None:
                yield period

    def _insert_record(self, record):
        return self._insert_user(record.to_user())

    def _known_user(self, user):
        return user.get_uid() in self._records_by_user

    def _unknown_user(self, user):
        return not self._known_user(user)

    def _insert_user(self, user):
        if user not in self or self[user].is_offline():
            self[user] = user
            #print(2)
            return None
        if user.is_online():
            #print(3)
            print(user._fields)
            return None
        period = user, self[user].get_last_seen_time(), user.get_last_seen_time()
        self[user] = user
        return period
