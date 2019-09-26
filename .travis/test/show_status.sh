#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

show_status() {
    echo 'Running show_status.py...'
    python3 -m bin.show_status "$@"
}

main() {
    show_status egor.tensin
}

main "$@"
