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

from vk.user import UserField

def process_database(db_reader, writer):
    from vk.utils.tracking import OnlinePeriodEnumerator
    wasted_time_by_user = {}
    for online_period in OnlinePeriodEnumerator().enum(db_reader):
        user, time_from, time_to = online_period
        if user not in wasted_time_by_user:
            wasted_time_by_user[user] = timedelta()
        wasted_time_by_user[user] = time_to - time_from
    for user, wasted_time in wasted_time_by_user.items():
        writer.write_wasted_time(user, wasted_time)

class DatabaseFormat(Enum):
    CSV = 'csv'

    def __str__(self):
        return self.value

def open_database_csv(path):
    from vk.utils.tracking.db.reader.csv import Reader
    return Reader(path)

def open_database(path, fmt):
    if fmt is DatabaseFormat.CSV:
        return open_database_csv(path)
    else:
        raise NotImplementedError('unsupported database format: ' + str(fmt))

class OutputFormat(Enum):
    CSV = 'csv'
    JSON = 'json'
    IMG = 'img'

    def __str__(self):
        return self.value

OUTPUT_USER_FIELDS = (
    UserField.UID,
    UserField.FIRST_NAME,
    UserField.LAST_NAME,
    UserField.SCREEN_NAME,
)

class OutputWriterCSV:
    def __init__(self, fd=sys.stdout):
        self._writer = csv.writer(fd, lineterminator='\n')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def write_wasted_time(self, user, wasted_time):
        self._write_row(self._wasted_time_to_row(user, wasted_time))

    def _write_row(self, row):
        self._writer.writerow(row)

    @staticmethod
    def _wasted_time_to_row(user, wasted_time):
        row = []
        for field in OUTPUT_USER_FIELDS:
            row.append(user[field])
        row.append(str(wasted_time))
        return row

class OutputWriterJSON:
    def __init__(self, fd=sys.stdout):
        self._fd = fd
        self._records = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._fd.write(json.dumps(self._records, indent=3))

    def write_wasted_time(self, user, wasted_time):
        self._records.append(self._wasted_time_to_record(user, wasted_time))

    _WASTED_TIME_FIELD = 'wasted_time'

    @staticmethod
    def _wasted_time_to_record(user, wasted_time):
        record = OrderedDict()
        for field in OUTPUT_USER_FIELDS:
            record[str(field)] = user[field]
        record[OutputWriterJSON._WASTED_TIME_FIELD] = str(wasted_time)
        return record

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
        self._wasted_time_by_user = {}
        self._fd = fd
        pass

    def __enter__(self):
        return self

    @staticmethod
    def _format_user_name(user):
        return '{}\n{}'.format(user.get_first_name(), user.get_last_name())

    @staticmethod
    def _format_wasted_time(seconds, _):
        return str(timedelta(seconds=seconds))

    @staticmethod
    def _wasted_time_to_seconds(td):
        return td.total_seconds()

    def _get_user_names(self):
        return tuple(map(self._format_user_name, self._wasted_time_by_user.keys()))

    def _get_wasted_seconds(self):
        return tuple(map(self._wasted_time_to_seconds, self._wasted_time_by_user.values()))

    def __exit__(self, *args):
        bar_chart = BarChartBuilder()

        bar_chart.set_title('How much time do people spend online?')
        bar_chart.set_value_grid()

        bar_chart.set_integer_values_only()
        bar_chart.set_property(bar_chart.get_value_labels(),
                               fontsize='small', rotation=30)
        bar_chart.set_value_label_formatter(self._format_wasted_time)

        users = self._get_user_names()
        wasted_time = self._get_wasted_seconds()

        if not self._wasted_time_by_user or not max(wasted_time):
            bar_chart.set_value_axis_limits(0)

        bars = bar_chart.plot_bars(users, wasted_time)
        bar_chart.set_property(bars, alpha=.33)

        if self._fd is sys.stdout:
            bar_chart.show()
        else:
            bar_chart.save(self._fd)

    def write_wasted_time(self, user, wasted_time):
        #if len(self._wasted_time_by_user) >= 1:
        #    return
        #if wasted_time.total_seconds():
        #    return
        self._wasted_time_by_user[user] = wasted_time # + timedelta(seconds=3)

def open_output_writer_csv(fd):
    return OutputWriterCSV(fd)

def open_output_writer_json(fd):
    return OutputWriterJSON(fd)

def open_output_writer_img(fd):
    return PlotBuilder(fd)

def open_output_writer(fd, fmt):
    if fmt is OutputFormat.CSV:
        return open_output_writer_csv(fd)
    elif fmt is OutputFormat.JSON:
        return open_output_writer_json(fd)
    elif fmt is OutputFormat.IMG:
        return open_output_writer_img(fd)
    else:
        raise NotImplementedError('unsupported output type: ' + str(fmt))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

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

    parser.add_argument('input', help='database path')
    parser.add_argument('output', type=argparse.FileType('w'),
                        nargs='?', default=sys.stdout,
                        help='output path (standard output by default)')
    parser.add_argument('--input-format', type=database_format,
                        choices=tuple(str(fmt) for fmt in DatabaseFormat),
                        default=DatabaseFormat.CSV,
                        help='specify database format')
    parser.add_argument('--output-format', type=output_format,
                        choices=tuple(fmt for fmt in OutputFormat),
                        default=OutputFormat.CSV,
                        help='specify output format')

    args = parser.parse_args()

    with open_database(args.input, args.input_format) as db_reader:
        with open_output_writer(args.output, args.output_format) as output_writer:
            process_database(db_reader, output_writer)
