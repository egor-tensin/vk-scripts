# Copyright (c) 2017 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

import abc
from collections.abc import Iterable


class Writer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_initial_status(self, user):
        pass

    @abc.abstractmethod
    def on_status_update(self, user):
        pass

    @abc.abstractmethod
    def on_connection_error(self, e):
        pass


class Reader(Iterable, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __iter__(self):
        pass
