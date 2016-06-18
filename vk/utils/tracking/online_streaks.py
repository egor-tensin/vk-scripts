# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import timedelta

from vk.user import User

class OnlineStreakEnumerator(MutableMapping):
    def __init__(self):
        self._records = {}

    def __getitem__(self, user):
        return self._records[user]

    def __setitem__(self, user, record):
        self._records[user] = record

    def __delitem__(self, user):
        del self._records[user]

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)

    def enum(self, db_reader):
        for record in db_reader:
            period = self._insert_record(record)
            if period is not None:
                yield period

    def group_by_user(self, db_reader):
        by_user = {}
        for user, time_from, time_to in self.enum(db_reader):
            if user not in by_user:
                by_user[user] = timedelta()
            by_user[user] += time_to - time_from
        return by_user

    def group_by_date(self, db_reader):
        by_date = OrderedDict()
        for _, time_from, time_to in self.enum(db_reader):
            for date, duration in self._enum_dates_and_durations(time_from, time_to):
                if date not in by_date:
                    by_date[date] = timedelta()
                by_date[date] += duration
        return by_date

    def group_by_weekday(self, db_reader):
        by_weekday = OrderedDict()
        for weekday in range(7):
            by_weekday[weekday] = timedelta()
        for _, time_from, time_to in self.enum(db_reader):
            for date, duration in self._enum_dates_and_durations(time_from, time_to):
                by_weekday[date.weekday()] += duration
        return by_weekday

    @staticmethod
    def _enum_dates_and_durations(time_from, time_to):
        while time_from.date() != time_to.date():
            next_day = time_from.date() + timedelta(days=1)
            yield time_from.date(), next_day - time_from
            time_from = next_day
        yield time_to.date(), time_to - time_from

    def _insert_record(self, record):
        return self._insert_user(record.to_user())

    def _known_user(self, user):
        return user.get_uid() in self._records

    def _unknown_user(self, user):
        return not self._known_user(user)

    def _insert_user(self, user):
        if user not in self or self[user].is_offline():
            self[user] = user
            return None
        if user.is_online():
            print(user._fields)
            return None
        period = user, self[user].get_last_seen_time(), user.get_last_seen_time()
        self[user] = user
        return period
