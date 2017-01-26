# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from collections.abc import Iterable

class Writer:
    def __init__(self):
        pass

    def on_initial_status(self, user):
        pass

    def on_status_update(self, user):
        pass

    def on_connection_error(self, e):
        pass

class Reader(Iterable):
    def __init__(self):
        pass

    def __iter__(self):
        pass
