# Copyright (c) 2017 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import matplotlib.pyplot as plt
import numpy as np

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

if __name__ == '__main__':
    builder = BarChartBuilder()
    builder.plot_bars(['Name #1', 'Name #2', 'Name #3'], [4, 11, 7])
    builder.show()
