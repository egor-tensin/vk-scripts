# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.


class APIError(RuntimeError):
    pass


class InvalidAPIResponseError(APIError):
    def __init__(self, response):
        super().__init__()
        self.response = response

    def __str__(self):
        return str(self.response)


class APIConnectionError(APIError):
    pass
