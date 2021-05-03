# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import abc
import argparse
from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import datetime, timedelta, timezone
from enum import Enum
import sys

from vk.tracking.db import Format as DatabaseFormat
from vk.user import UserField
from vk.utils.bar_chart import BarChartBuilder
from vk.utils import io


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


class GroupBy(Enum):
    USER = 'user'
    DATE = 'date'
    WEEKDAY = 'weekday'
    HOUR = 'hour'

    def __str__(self):
        return self.value

    def group(self, db_reader, time_from=None, time_to=None):
        online_streaks = OnlineSessionEnumerator(time_from, time_to)
        if self is GroupBy.USER:
            return online_streaks.group_by_user(db_reader)
        if self is GroupBy.DATE:
            return online_streaks.group_by_date(db_reader)
        if self is GroupBy.WEEKDAY:
            return online_streaks.group_by_weekday(db_reader)
        if self is GroupBy.HOUR:
            return online_streaks.group_by_hour(db_reader)
        raise NotImplementedError('unsupported grouping: ' + str(self))


_OUTPUT_USER_FIELDS = (
    UserField.UID,
    UserField.FIRST_NAME,
    UserField.LAST_NAME,
    UserField.DOMAIN,
)


class OutputSinkOnlineSessions(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def process_database(self, group_by, db_reader, time_from=None, time_to=None):
        pass


class OutputConverterCSV:
    @staticmethod
    def convert_user(user):
        return [user[field] for field in _OUTPUT_USER_FIELDS]

    @staticmethod
    def convert_date(date):
        return [str(date)]

    @staticmethod
    def convert_weekday(weekday):
        return [str(weekday)]

    @staticmethod
    def convert_hour(hour):
        return [str(timedelta(hours=hour))]


class OutputSinkCSV(OutputSinkOnlineSessions):
    def __init__(self, fd=sys.stdout):
        self._writer = io.FileWriterCSV(fd)

    _CONVERT_KEY = {
        GroupBy.USER: OutputConverterCSV.convert_user,
        GroupBy.DATE: OutputConverterCSV.convert_date,
        GroupBy.WEEKDAY: OutputConverterCSV.convert_weekday,
        GroupBy.HOUR: OutputConverterCSV.convert_hour,
    }

    @staticmethod
    def _key_to_row(group_by, key):
        if group_by not in OutputSinkCSV._CONVERT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(group_by))
        return OutputSinkCSV._CONVERT_KEY[group_by](key)

    def process_database(self, group_by, db_reader, time_from=None, time_to=None):
        for key, duration in group_by.group(db_reader, time_from, time_to).items():
            row = self._key_to_row(group_by, key)
            row.append(str(duration))
            self._writer.write_row(row)


class OutputConverterJSON:
    _DATE_FIELD = 'date'
    _WEEKDAY_FIELD = 'weekday'
    _HOUR_FIELD = 'hour'

    assert _DATE_FIELD not in map(str, _OUTPUT_USER_FIELDS)
    assert _WEEKDAY_FIELD not in map(str, _OUTPUT_USER_FIELDS)
    assert _HOUR_FIELD not in map(str, _OUTPUT_USER_FIELDS)

    @staticmethod
    def convert_user(user):
        obj = OrderedDict()
        for field in _OUTPUT_USER_FIELDS:
            obj[str(field)] = user[field]
        return obj

    @staticmethod
    def convert_date(date):
        obj = OrderedDict()
        obj[OutputConverterJSON._DATE_FIELD] = str(date)
        return obj

    @staticmethod
    def convert_weekday(weekday):
        obj = OrderedDict()
        obj[OutputConverterJSON._WEEKDAY_FIELD] = str(weekday)
        return obj

    @staticmethod
    def convert_hour(hour):
        obj = OrderedDict()
        obj[OutputConverterJSON._HOUR_FIELD] = str(timedelta(hours=hour))
        return obj


class OutputSinkJSON(OutputSinkOnlineSessions):
    def __init__(self, fd=sys.stdout):
        self._writer = io.FileWriterJSON(fd)

    _DURATION_FIELD = 'duration'

    assert _DURATION_FIELD not in map(str, _OUTPUT_USER_FIELDS)

    _CONVERT_KEY = {
        GroupBy.USER: OutputConverterJSON.convert_user,
        GroupBy.DATE: OutputConverterJSON.convert_date,
        GroupBy.WEEKDAY: OutputConverterJSON.convert_weekday,
        GroupBy.HOUR: OutputConverterJSON.convert_hour,
    }

    @staticmethod
    def _key_to_object(group_by, key):
        if group_by not in OutputSinkJSON._CONVERT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(group_by))
        return OutputSinkJSON._CONVERT_KEY[group_by](key)

    def process_database(self, group_by, db_reader, time_from=None, time_to=None):
        entries = []
        for key, duration in group_by.group(db_reader, time_from, time_to).items():
            entry = self._key_to_object(group_by, key)
            entry[self._DURATION_FIELD] = str(duration)
            entries.append(entry)
        self._writer.write(entries)


class OutputConverterPlot:
    @staticmethod
    def convert_user(user):
        return '{}\n{}'.format(user.get_first_name(), user.get_last_name())

    @staticmethod
    def convert_date(date):
        return str(date)

    @staticmethod
    def convert_weekday(weekday):
        return str(weekday)

    @staticmethod
    def convert_hour(hour):
        return '{}:00'.format(hour)


class OutputSinkPlot(OutputSinkOnlineSessions):
    def __init__(self, fd=sys.stdout):
        self._fd = fd

    TITLE = 'How much time people spend online'

    _FORMAT_KEY = {
        GroupBy.USER: OutputConverterPlot.convert_user,
        GroupBy.DATE: OutputConverterPlot.convert_date,
        GroupBy.WEEKDAY: OutputConverterPlot.convert_weekday,
        GroupBy.HOUR: OutputConverterPlot.convert_hour,
    }

    @staticmethod
    def _format_key(group_by, key):
        if group_by not in OutputSinkPlot._FORMAT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(group_by))
        return OutputSinkPlot._FORMAT_KEY[group_by](key)

    @staticmethod
    def _format_duration(seconds, _):
        return str(timedelta(seconds=seconds))

    @staticmethod
    def _duration_to_seconds(td):
        return td.total_seconds()

    @staticmethod
    def _extract_labels(group_by, durations):
        return (OutputSinkPlot._format_key(group_by, key) for key in durations.keys())

    @staticmethod
    def _extract_values(durations):
        return (OutputSinkPlot._duration_to_seconds(duration) for duration in durations.values())

    def process_database(
            self, group_by, db_reader, time_from=None, time_to=None):

        durations = group_by.group(db_reader, time_from, time_to)

        bar_chart = BarChartBuilder()
        bar_chart.set_title(OutputSinkPlot.TITLE)
        bar_chart.enable_grid_for_values()
        bar_chart.only_integer_values()
        bar_chart.set_property(bar_chart.get_values_labels(),
                               fontsize='small', rotation=30)
        bar_chart.set_value_label_formatter(self._format_duration)

        labels = tuple(self._extract_labels(group_by, durations))
        durations = tuple(self._extract_values(durations))

        if group_by is GroupBy.HOUR:
            bar_chart.labels_align_middle = False
            bar_height = bar_chart.THIN_BAR_HEIGHT
        else:
            bar_height = bar_chart.THICK_BAR_HEIGHT

        bars = bar_chart.plot_bars(
            labels, durations, bar_height=bar_height)
        bar_chart.set_property(bars, alpha=.33)

        if self._fd is sys.stdout:
            bar_chart.show()
        else:
            bar_chart.save(self._fd)


class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'
    PLOT = 'plot'

    def __str__(self):
        return self.value

    def create_sink(self, fd=sys.stdout):
        if self is OutputFormat.CSV:
            return OutputSinkCSV(fd)
        if self is OutputFormat.JSON:
            return OutputSinkJSON(fd)
        if self is OutputFormat.PLOT:
            return OutputSinkPlot(fd)
        raise NotImplementedError('unsupported output format: ' + str(self))

    def open_file(self, path=None):
        if self is OutputFormat.PLOT:
            return io.open_output_binary_file(path)
        return io.open_output_text_file(path)


def _parse_group_by(s):
    try:
        return GroupBy(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid "group by" value: ' + s)


def _parse_database_format(s):
    try:
        return DatabaseFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid database format: ' + s)


def _parse_output_format(s):
    try:
        return OutputFormat(s)
    except ValueError:
        raise argparse.ArgumentTypeError('invalid output format: ' + s)


_DATE_RANGE_LIMIT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def _parse_date_range_limit(s):
    try:
        dt = datetime.strptime(s, _DATE_RANGE_LIMIT_FORMAT)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        msg = 'invalid date range limit (must be in the \'{}\' format): {}'
        raise argparse.ArgumentTypeError(
            msg.format(_DATE_RANGE_LIMIT_FORMAT, s))


def _parse_args(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='View/visualize the amount of time people spend online.')

    parser.add_argument('db_path', metavar='input', nargs='?',
                        help='database file path (standard input by default)')
    parser.add_argument('out_path', metavar='output', nargs='?',
                        help='output file path (standard output by default)')
    parser.add_argument('-g', '--group-by',
                        type=_parse_group_by,
                        choices=GroupBy,
                        default=GroupBy.USER,
                        help='group online sessions by user/date/etc.')
    parser.add_argument('-i', '--input-format', dest='db_fmt',
                        type=_parse_database_format,
                        default=DatabaseFormat.CSV,
                        choices=DatabaseFormat,
                        help='specify database format')
    parser.add_argument('-o', '--output-format', dest='out_fmt',
                        type=_parse_output_format,
                        choices=OutputFormat,
                        default=OutputFormat.CSV,
                        help='specify output format')
    parser.add_argument('-a', '--from', dest='time_from',
                        type=_parse_date_range_limit, default=None,
                        help='discard online activity prior to this moment')
    parser.add_argument('-b', '--to', dest='time_to',
                        type=_parse_date_range_limit, default=None,
                        help='discard online activity after this moment')

    return parser.parse_args(args)


def process_online_sessions(
        db_path=None, db_fmt=DatabaseFormat.CSV,
        out_path=None, out_fmt=OutputFormat.CSV,
        group_by=GroupBy.USER,
        time_from=None, time_to=None):

    if time_from is not None and time_to is not None:
        if time_from > time_to:
            time_from, time_to = time_to, time_from

    with db_fmt.open_input_file(db_path) as db_fd:
        db_reader = db_fmt.create_reader(db_fd)
        with out_fmt.open_file(out_path) as out_fd:
            out_sink = out_fmt.create_sink(out_fd)
            out_sink.process_database(
                group_by, db_reader,
                time_from=time_from,
                time_to=time_to)


def main(args=None):
    process_online_sessions(**vars(_parse_args(args)))


if __name__ == '__main__':
    main()
