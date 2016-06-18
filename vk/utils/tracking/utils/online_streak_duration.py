# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import csv
from collections import OrderedDict
from datetime import timedelta
from enum import Enum
import json
import sys

import matplotlib.pyplot as plt
import numpy as np

from ..online_streaks import OnlineStreakEnumerator, Weekday
from ..db import Format as DatabaseFormat
from vk.user import UserField

class Grouping(Enum):
    USER = 'user'
    DATE = 'date'
    WEEKDAY = 'weekday'

    def enum_durations(self, db_reader):
        if self is Grouping.USER:
            return OnlineStreakEnumerator().group_by_user(db_reader)
        elif self is Grouping.DATE:
            return OnlineStreakEnumerator().group_by_date(db_reader)
        elif self is Grouping.WEEKDAY:
            return OnlineStreakEnumerator().group_by_weekday(db_reader)
        else:
            raise NotImplementedError('unsupported grouping: ' + str(self))

    def __str__(self):
        return self.value

_USER_FIELDS = (
    UserField.UID,
    UserField.FIRST_NAME,
    UserField.LAST_NAME,
    UserField.SCREEN_NAME,
)

class OutputWriterCSV:
    def __init__(self, fd=sys.stdout):
        self._writer = csv.writer(fd, lineterminator='\n')

    def _user_to_row(user):
        return [user[field] for field in _USER_FIELDS]

    def _date_to_row(date):
        return [str(date)]

    def _weekday_to_row(weekday):
        return [str(weekday)]

    _CONVERT_KEY_TO_ROW = {
        Grouping.USER: _user_to_row,
        Grouping.DATE: _date_to_row,
        Grouping.WEEKDAY: _weekday_to_row,
    }

    @staticmethod
    def _key_to_row(grouping, key):
        if grouping not in OutputWriterCSV._CONVERT_KEY_TO_ROW:
            raise NotImplementedError('unsupported grouping: ' + str(grouping))
        return OutputWriterCSV._CONVERT_KEY_TO_ROW[grouping](key)

    def process_database(self, grouping, db_reader):
        for key, duration in grouping.enum_durations(db_reader).items():
            row = self._key_to_row(grouping, key)
            row.append(str(duration))
            self._write_row(row)

    def _write_row(self, row):
        self._writer.writerow(row)

_DATE_FIELD = 'date'
_WEEKDAY_FIELD = 'weekday'

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd

    def _user_to_object(user):
        obj = OrderedDict()
        for field in _USER_FIELDS:
            obj[str(field)] = user[field]
        return obj

    def _date_to_object(date):
        obj = OrderedDict()
        obj[_DATE_FIELD] = str(date)
        return obj

    def _weekday_to_object(weekday):
        obj = OrderedDict()
        obj[_WEEKDAY_FIELD] = str(weekday)
        return obj

    _DURATION_FIELD = 'duration'

    _CONVERT_KEY_TO_OBJECT = {
        Grouping.USER: _user_to_object,
        Grouping.DATE: _date_to_object,
        Grouping.WEEKDAY: _weekday_to_object,
    }

    @staticmethod
    def _key_to_object(grouping, key):
        if not grouping in OutputWriterJSON._CONVERT_KEY_TO_OBJECT:
            raise NotImplementedError('unsupported grouping: ' + str(grouping))
        return OutputWriterJSON._CONVERT_KEY_TO_OBJECT[grouping](key)

    def process_database(self, grouping, db_reader):
        arr = []
        for key, duration in grouping.enum_durations(db_reader).items():
            obj = self._key_to_object(grouping, key)
            obj[self._DURATION_FIELD] = str(duration)
            arr.append(obj)
        self._fd.write(json.dumps(arr, indent=3))

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

    def set_property(self, *args, **kwargs):
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

    def plot_bars(self, bar_labels, values):
        numof_bars = len(bar_labels)

        if not numof_bars:
            self.set_height(1)
            self._get_bar_axis().set_tick_params(labelleft=False)
            return []

        self.set_height(numof_bars)

        bar_offsets = np.arange(numof_bars) * 2 * self._BAR_HEIGHT + self._BAR_HEIGHT
        bar_axis_min, bar_axis_max = 0, 2 * self._BAR_HEIGHT * numof_bars

        self._get_bar_axis().set_ticks(bar_offsets)
        self._get_bar_axis().set_ticklabels(bar_labels)
        self.set_bar_axis_limits(bar_axis_min, bar_axis_max)

        return self._ax.barh(bar_offsets, values, align='center', height=self._BAR_HEIGHT)

    def show(self):
        plt.show()

    def save(self, path):
        self._fig.savefig(path, bbox_inches='tight')

class PlotBuilder:
    def __init__(self, fd=sys.stdout):
        self._fd = fd

    def _format_user(user):
        return '{}\n{}'.format(user.get_first_name(), user.get_last_name())

    def _format_date(date):
        return str(date)

    def _format_weekday(weekday):
        return str(weekday)

    _FORMAT_KEY = {
        Grouping.USER: _format_user,
        Grouping.DATE: _format_date,
        Grouping.WEEKDAY: _format_weekday,
    }

    @staticmethod
    def _format_key(grouping, key):
        if grouping not in PlotBuilder._FORMAT_KEY:
            raise NotImplementedError('unsupported grouping: ' + str(grouping))
        return PlotBuilder._FORMAT_KEY[grouping](key)

    @staticmethod
    def _format_duration(seconds, _):
        return str(timedelta(seconds=seconds))

    @staticmethod
    def _duration_to_seconds(td):
        return td.total_seconds()

    @staticmethod
    def _extract_labels(grouping, durations):
        return tuple(map(lambda key: PlotBuilder._format_key(grouping, key), durations.keys()))

    @staticmethod
    def _extract_values(durations):
        return tuple(map(PlotBuilder._duration_to_seconds, durations.values()))

    def process_database(self, grouping, db_reader):
        durations = grouping.enum_durations(db_reader)

        bar_chart = BarChartBuilder()

        bar_chart.set_title('How much time people spend online?')
        bar_chart.set_value_grid()

        bar_chart.set_integer_values_only()
        bar_chart.set_property(bar_chart.get_value_labels(),
                               fontsize='small', rotation=30)
        bar_chart.set_value_label_formatter(self._format_duration)

        labels = self._extract_labels(grouping, durations)
        durations = self._extract_values(durations)

        if not labels or not max(durations):
            bar_chart.set_value_axis_limits(0)

        bars = bar_chart.plot_bars(labels, durations)
        bar_chart.set_property(bars, alpha=.33)

        if self._fd is sys.stdout:
            bar_chart.show()
        else:
            bar_chart.save(self._fd)

class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'
    IMG = 'img'

    def create_writer(self, fd):
        if self is OutputFormat.CSV:
            return OutputWriterCSV(fd)
        elif self is OutputFormat.JSON:
            return OutputWriterJSON(fd)
        elif self is OutputFormat.IMG:
            return PlotBuilder(fd)
        else:
            raise NotImplementedError('unsupported output format: ' + str(self))

    def __str__(self):
        return self.value

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    def grouping(s):
        try:
            return Grouping(s)
        except ValueError:
            raise argparse.ArgumentTypeError()
    def database_format(s):
        try:
            return DatabaseFormat(s)
        except ValueError:
            raise argparse.ArgumentTypeError()
    def output_format(s):
        try:
            return OutputFormat(s)
        except ValueError:
            raise argparse.ArgumentTypeError()

    parser.add_argument('input', type=argparse.FileType('r'),
                        help='database path')
    parser.add_argument('output', type=argparse.FileType('w'),
                        nargs='?', default=sys.stdout,
                        help='output path (standard output by default)')
    parser.add_argument('--grouping', type=grouping,
                        choices=tuple(grouping for grouping in Grouping),
                        default=Grouping.USER,
                        help='set grouping')
    parser.add_argument('--input-format', type=database_format,
                        choices=tuple(fmt for fmt in DatabaseFormat),
                        default=DatabaseFormat.CSV,
                        help='specify database format')
    parser.add_argument('--output-format', type=output_format,
                        choices=tuple(fmt for fmt in OutputFormat),
                        default=OutputFormat.CSV,
                        help='specify output format')

    args = parser.parse_args()

    with args.input_format.create_reader(args.input) as db_reader:
        output_writer = args.output_format.create_writer(args.output)
        output_writer.process_database(args.grouping, db_reader)
