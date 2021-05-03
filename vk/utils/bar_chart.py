# Copyright (c) 2017 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np


class BarChartBuilder:
    _BAR_HEIGHT = .5

    THICK_BAR_HEIGHT = _BAR_HEIGHT
    THIN_BAR_HEIGHT = THICK_BAR_HEIGHT / 2

    def __init__(self, labels_align_middle=True):
        self._fig, self._ax = plt.subplots()
        self.labels_align_middle = labels_align_middle

    def set_title(self, title):
        self._ax.set_title(title)

    def _get_categories_axis(self):
        return self._ax.get_yaxis()

    def _get_values_axis(self):
        return self._ax.get_xaxis()

    def set_categories_axis_limits(self, start=None, end=None):
        bottom, top = self._ax.get_ylim()
        if start is not None:
            bottom = start
        if end is not None:
            top = end
        self._ax.set_ylim(bottom=bottom, top=top)

    def set_values_axis_limits(self, start=None, end=None):
        left, right = self._ax.get_xlim()
        if start is not None:
            left = start
        if end is not None:
            right = end
        self._ax.set_xlim(left=left, right=right)

    def enable_grid_for_categories(self):
        self._get_categories_axis().grid()

    def enable_grid_for_values(self):
        self._get_values_axis().grid()

    def get_categories_labels(self):
        return self._get_categories_axis().get_ticklabels()

    def get_values_labels(self):
        return self._get_values_axis().get_ticklabels()

    def hide_categories(self):
        self._get_categories_axis().set_major_locator(ticker.NullLocator())

    def set_value_label_formatter(self, fn):
        self._get_values_axis().set_major_formatter(ticker.FuncFormatter(fn))

    def any_values(self):
        self._get_values_axis().set_major_locator(ticker.AutoLocator())

    def only_integer_values(self):
        self._get_values_axis().set_major_locator(ticker.MaxNLocator(integer=True))

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

    _DEFAULT_VALUES_AXIS_MAX = 1
    assert _DEFAULT_VALUES_AXIS_MAX > 0

    def plot_bars(self, categories, values, bar_height=THICK_BAR_HEIGHT):
        numof_bars = len(categories)
        inches_per_bar = 2 * bar_height
        categories_axis_max = inches_per_bar * numof_bars

        if not numof_bars:
            categories_axis_max += inches_per_bar

        self.set_height(categories_axis_max)
        self.set_categories_axis_limits(0, categories_axis_max)

        if not numof_bars:
            self.set_values_axis_limits(0, self._DEFAULT_VALUES_AXIS_MAX)
            self.hide_categories()
            return []

        bar_offset = inches_per_bar / 2
        bar_offsets = inches_per_bar * np.arange(numof_bars) + bar_offset

        if self.labels_align_middle:
            self._get_categories_axis().set_ticks(bar_offsets)
        else:
            self._get_categories_axis().set_ticks(bar_offsets - bar_offset)

        self._get_categories_axis().set_ticklabels(categories)

        bars = self._ax.barh(bar_offsets, values, align='center',
                             height=bar_height)

        if min(values) >= 0:
            self.set_values_axis_limits(start=0)
            if np.isclose(max(values), 0.):
                self.set_values_axis_limits(end=self._DEFAULT_VALUES_AXIS_MAX)
        elif max(values) < 0:
            self.set_values_axis_limits(end=0)

        return bars

    @staticmethod
    def show():
        plt.show()

    def save(self, path):
        self._fig.savefig(path, bbox_inches='tight')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--categories', nargs='*', metavar='LABEL',
                        default=[])
    parser.add_argument('--values', nargs='*', metavar='N',
                        default=[], type=float)

    parser.add_argument('--output', '-o', help='set output file path')

    parser.add_argument('--align-middle', action='store_true',
                        dest='labels_align_middle',
                        help='align labels to the middle of the bars')

    parser.add_argument('--integer-values', action='store_true',
                        dest='only_integer_values')
    parser.add_argument('--any-values', action='store_false',
                        dest='only_integer_values')

    parser.add_argument('--grid-categories', action='store_true')
    parser.add_argument('--grid-values', action='store_true')

    args = parser.parse_args()

    if len(args.categories) < len(args.values):
        parser.error('too many bar values')
    if len(args.categories) > len(args.values):
        args.values.extend([0.] * (len(args.categories) - len(args.values)))

    builder = BarChartBuilder(labels_align_middle=args.labels_align_middle)

    if args.only_integer_values:
        builder.only_integer_values()
    else:
        builder.any_values()

    if args.grid_categories:
        builder.enable_grid_for_categories()
    if args.grid_values:
        builder.enable_grid_for_values()

    builder.plot_bars(args.categories, args.values)

    if args.output is None:
        builder.show()
    else:
        builder.save(args.output)
