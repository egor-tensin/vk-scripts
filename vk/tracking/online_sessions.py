# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import timedelta
from enum import Enum


class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __str__(self):
        return self.name[0] + self.name[1:].lower()


class OnlineSessionEnumerator(MutableMapping):
    def __init__(self, time_from=None, time_to=None):
        self._records = {}
        self._time_from = time_from
        self._time_to = time_to

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

    def _trim_or_drop_session(self, session):
        user, started_at, ended_at = session
        if self._time_from is not None:
            if ended_at < self._time_from:
                return None
            if started_at < self._time_from:
                started_at = self._time_from
        if self._time_to is not None:
            if started_at > self._time_to:
                return None
            if ended_at > self._time_to:
                ended_at = self._time_to
        return user, started_at, ended_at

    def read_database(self, db_reader):
        for record in db_reader:
            session = self._process_database_record(record)
            if session is not None:
                session = self._trim_or_drop_session(session)
            if session is not None:
                yield session

    def group_by_user(self, db_reader):
        by_user = {}
        for user, started_at, ended_at in self.read_database(db_reader):
            if user not in by_user:
                by_user[user] = timedelta()
            by_user[user] += ended_at - started_at
        return by_user

    def group_by_date(self, db_reader):
        by_date = {}
        for _, started_at, ended_at in self.read_database(db_reader):
            for date, duration in self._split_into_days(started_at, ended_at):
                if date not in by_date:
                    by_date[date] = timedelta()
                by_date[date] += duration
        return by_date

    def group_by_weekday(self, db_reader):
        by_weekday = OrderedDict()
        for weekday in Weekday:
            by_weekday[weekday] = timedelta()
        for _, started_at, ended_at in self.read_database(db_reader):
            for date, duration in self._split_into_days(started_at, ended_at):
                by_weekday[Weekday(date.weekday())] += duration
        return by_weekday

    def group_by_hour(self, db_reader):
        by_hour = OrderedDict()
        for i in range(24):
            by_hour[i] = timedelta()
        for _, started_at, ended_at in self.read_database(db_reader):
            for hour, duration in self._split_into_hours(started_at, ended_at):
                by_hour[hour] += duration
        return by_hour

    @staticmethod
    def _split_into_days(a, b):
        while a.date() != b.date():
            next_day = a.date() + timedelta(days=1)
            yield a.date(), next_day - a
            a = next_day
        yield b.date(), b - a

    @staticmethod
    def _split_into_hours(a, b):
        while a.date() != b.date() or a.hour != b.hour:
            next_hour = a.replace(minute=0, second=0) + timedelta(hours=1)
            yield a.hour, next_hour - a
            a = next_hour
        yield b.hour, b - a

    def _process_database_record(self, record):
        return self._close_user_session(record.to_user())

    def _known_user(self, user):
        return user.get_uid() in self._records

    def _unknown_user(self, user):
        return not self._known_user(user)

    def _close_user_session(self, user):
        if user not in self or self[user].is_offline():
            self[user] = user
            return None
        if user.is_online():
            return None
        session = user, self[user].get_last_seen_time(), user.get_last_seen_time()
        self[user] = user
        return session
