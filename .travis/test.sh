#!/usr/bin/env bash

# Copyright (c) 2020 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

run_test() {
    local arg
    echo
    echo ======================================================================
    for arg; do
        echo -n "$arg "
    done
    echo
    echo ======================================================================

    python3 -m "$@"
}

run_test "$@"
