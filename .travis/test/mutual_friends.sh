#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

mutual_friends() {
    echo 'Running mutual_friends.py --format csv...'
    python3 -m bin.mutual_friends --format csv "$@"
    echo 'Running mutual_friends.py --format json...'
    python3 -m bin.mutual_friends --format json "$@"
}

main() {
    mutual_friends kreed58 maxkorzh_official
}

main "$@"
