# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import argparse
import csv
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
import sys

from vk.tracking import OnlineSessionEnumerator
from vk.tracking.db import Format as DatabaseFormat
from vk.user import UserField

from .utils.bar_chart import BarChartBuilder

class GroupBy(Enum):
    USER = 'user'
    DATE = 'date'
    WEEKDAY = 'weekday'
    HOUR = 'hour'

    def group(self, db_reader, time_from=None, time_to=None):
        online_streaks = OnlineSessionEnumerator(time_from, time_to)
        if self is GroupBy.USER:
            return online_streaks.group_by_user(db_reader)
        elif self is GroupBy.DATE:
            return online_streaks.group_by_date(db_reader)
        elif self is GroupBy.WEEKDAY:
            return online_streaks.group_by_weekday(db_reader)
        elif self is GroupBy.HOUR:
            return online_streaks.group_by_hour(db_reader)
        else:
            raise NotImplementedError('unsupported grouping: ' + str(self))

    def __str__(self):
        return self.value

_OUTPUT_USER_FIELDS = (
    UserField.UID,
    UserField.FIRST_NAME,
    UserField.LAST_NAME,
    UserField.DOMAIN,
)

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

class OutputWriterCSV:
    def __init__(self, fd=sys.stdout):
        self._writer = csv.writer(fd, lineterminator='\n')

    _CONVERT_KEY = {
        GroupBy.USER: OutputConverterCSV.convert_user,
        GroupBy.DATE: OutputConverterCSV.convert_date,
        GroupBy.WEEKDAY: OutputConverterCSV.convert_weekday,
        GroupBy.HOUR: OutputConverterCSV.convert_hour,
    }

    @staticmethod
    def _key_to_row(group_by, key):
        if group_by not in OutputWriterCSV._CONVERT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(group_by))
        return OutputWriterCSV._CONVERT_KEY[group_by](key)

    def process_database(self, group_by, db_reader, time_from=None, time_to=None):
        for key, duration in group_by.group(db_reader, time_from, time_to).items():
            row = self._key_to_row(group_by, key)
            row.append(str(duration))
            self._write_row(row)

    def _write_row(self, row):
        self._writer.writerow(row)

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

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd

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
        if not group_by in OutputWriterJSON._CONVERT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(group_by))
        return OutputWriterJSON._CONVERT_KEY[group_by](key)

    def _write(self, entries):
        self._fd.write(json.dumps(entries, indent=3, ensure_ascii=False))
        self._fd.write('\n')

    def process_database(self, group_by, db_reader, time_from=None, time_to=None):
        entries = []
        for key, duration in group_by.group(db_reader, time_from, time_to).items():
            entry = self._key_to_object(group_by, key)
            entry[self._DURATION_FIELD] = str(duration)
            entries.append(entry)
        self._write(entries)

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

class OutputWriterPlot:
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
        if group_by not in OutputWriterPlot._FORMAT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(group_by))
        return OutputWriterPlot._FORMAT_KEY[group_by](key)

    @staticmethod
    def _format_duration(seconds, _):
        return str(timedelta(seconds=seconds))

    @staticmethod
    def _duration_to_seconds(td):
        return td.total_seconds()

    @staticmethod
    def _extract_labels(group_by, durations):
        return tuple(map(lambda key: OutputWriterPlot._format_key(group_by, key), durations.keys()))

    @staticmethod
    def _extract_values(durations):
        return tuple(map(OutputWriterPlot._duration_to_seconds, durations.values()))

    def process_database(
            self, group_by, db_reader, time_from=None, time_to=None):

        durations = group_by.group(db_reader, time_from, time_to)

        bar_chart = BarChartBuilder()

        bar_chart.set_title(OutputWriterPlot.TITLE)
        bar_chart.set_value_grid()

        bar_chart.set_integer_values_only()
        bar_chart.set_property(
            bar_chart.get_value_labels(), fontsize='small', rotation=30)
        bar_chart.set_value_label_formatter(self._format_duration)

        labels = self._extract_labels(group_by, durations)
        durations = self._extract_values(durations)

        if not labels or not max(durations):
            bar_chart.set_value_axis_limits(0)

        bars = bar_chart.plot_bars(
            labels, durations,
            bars_between_ticks=group_by is GroupBy.HOUR,
            inches_per_bar=.5 if group_by is GroupBy.HOUR else 1)
        bar_chart.set_property(bars, alpha=.33)

        if self._fd is sys.stdout:
            bar_chart.show()
        else:
            bar_chart.save(self._fd)

class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'
    PLOT = 'plot'

    def create_writer(self, fd):
        if self is OutputFormat.CSV:
            return OutputWriterCSV(fd)
        elif self is OutputFormat.JSON:
            return OutputWriterJSON(fd)
        elif self is OutputFormat.PLOT:
            return OutputWriterPlot(fd)
        else:
            raise NotImplementedError('unsupported output format: ' + str(self))

    def __str__(self):
        return self.value

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

    parser.add_argument('db_fd', metavar='input',
                        type=argparse.FileType('r', encoding='utf-8'),
                        help='database file path')
    parser.add_argument('fd', metavar='output', nargs='?',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout,
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
    parser.add_argument('-o', '--output-format', dest='fmt',
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
        db_fd, db_fmt=DatabaseFormat.CSV,
        fd=sys.stdout, fmt=OutputFormat.CSV,
        group_by=GroupBy.USER,
        time_from=None, time_to=None):

    if time_from is not None and time_to is not None:
        if time_from > time_to:
            time_from, time_to = time_to, time_from

    with db_fmt.create_reader(db_fd) as db_reader:
        output_writer = fmt.create_writer(fd)
        output_writer.process_database(
            group_by, db_reader, time_from=time_from, time_to=time_to)

def main(args=None):
    process_online_sessions(**vars(_parse_args(args)))

if __name__ == '__main__':
    main()
