# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

class APIError(RuntimeError):
    pass

class InvalidResponseError(APIError):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return str(self.response)

class ConnectionError(APIError):
    pass
