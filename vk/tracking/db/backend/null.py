# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from .. import meta


class Writer(meta.Writer):
    def __init__(self):
        pass

    def on_initial_status(self, user):
        pass

    def on_status_update(self, user):
        pass

    def on_connection_error(self, e):
        pass


class Reader(meta.Reader):
    def __init__(self):
        pass

    def __iter__(self):
        return iter(())
