# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import argparse
import csv
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
import sys

import matplotlib.pyplot as plt
import numpy as np

from vk.tracking import OnlineSessionEnumerator
from vk.tracking.db import Format as DatabaseFormat
from vk.user import UserField

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

    def _write(self, x):
        self._fd.write(json.dumps(x, indent=3, ensure_ascii=False))
        self._fd.write('\n')

    def process_database(self, group_by, db_reader, time_from=None, time_to=None):
        arr = []
        for key, duration in group_by.group(db_reader, time_from, time_to).items():
            obj = self._key_to_object(group_by, key)
            obj[self._DURATION_FIELD] = str(duration)
            arr.append(obj)
        self._write(arr)

class BarChartBuilder:
    _BAR_HEIGHT = 1.

    def __init__(self):
        self._fig, self._ax = plt.subplots()

    def set_title(self, title):
        self._ax.set_title(title)

    def _get_bar_axis(self):
        return self._ax.get_yaxis()

    def _get_value_axis(self):
        return self._ax.get_xaxis()

    def set_bar_axis_limits(self, start=None, end=None):
        self._ax.set_ylim(bottom=start, top=end)

    def set_value_axis_limits(self, start=None, end=None):
        self._ax.set_xlim(left=start, right=end)

    def set_value_grid(self):
        self._get_value_axis().grid()

    def get_bar_labels(self):
        return self._get_bar_axis().get_ticklabels()

    def get_value_labels(self):
        return self._get_value_axis().get_ticklabels()

    def set_value_label_formatter(self, fn):
        from matplotlib.ticker import FuncFormatter
        self._get_value_axis().set_major_formatter(FuncFormatter(fn))

    def set_integer_values_only(self):
        from matplotlib.ticker import MaxNLocator
        self._get_value_axis().set_major_locator(MaxNLocator(integer=True))

    @staticmethod
    def set_property(*args, **kwargs):
        plt.setp(*args, **kwargs)

    def _set_size(self, inches, dim=0):
        fig_size = self._fig.get_size_inches()
        assert len(fig_size) == 2
        fig_size[dim] = inches
        self._fig.set_size_inches(fig_size, forward=True)

    def set_width(self, inches):
        self._set_size(inches)

    def set_height(self, inches):
        self._set_size(inches, dim=1)

    def plot_bars(
            self, bar_labels, bar_lengths,
            bars_between_ticks=False,
            inches_per_bar=1):

        numof_bars = len(bar_labels)

        if not numof_bars:
            self.set_height(1)
            self._get_bar_axis().set_tick_params(labelleft=False)
            return []

        self.set_height(inches_per_bar * numof_bars)

        bar_offsets = np.arange(numof_bars) * 2 * self._BAR_HEIGHT + self._BAR_HEIGHT

        if bars_between_ticks:
            self._get_bar_axis().set_ticks(bar_offsets - self._BAR_HEIGHT)
        else:
            self._get_bar_axis().set_ticks(bar_offsets)

        bar_axis_min = 0
        bar_axis_max = 2 * self._BAR_HEIGHT * numof_bars
        self.set_bar_axis_limits(bar_axis_min, bar_axis_max)

        self._get_bar_axis().set_ticklabels(bar_labels)

        return self._ax.barh(
            bar_offsets, bar_lengths, align='center', height=self._BAR_HEIGHT)

    @staticmethod
    def show():
        plt.show()

    def save(self, path):
        self._fig.savefig(path, bbox_inches='tight')

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

def _parse_args(args=sys.argv):
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

    return parser.parse_args(args[1:])

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

def main(args=sys.argv):
    args = _parse_args(args)
    process_online_sessions(**vars(args))

if __name__ == '__main__':
    main()
