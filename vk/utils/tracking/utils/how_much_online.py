# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from vk.utils.tracking import OnlinePeriodEnumerator
from vk.utils.tracking.db.reader import *

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('input', help='status database path')

    args = parser.parse_args()

    with csv.Reader(args.input) as csv_reader:
        for online_period in OnlinePeriodEnumerator().enum(csv_reader):
            user, dt_from, dt_to = online_period
            print(user.get_screen_name(), dt_from.isoformat(), dt_to.isoformat())
