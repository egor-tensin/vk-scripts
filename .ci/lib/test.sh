#!/usr/bin/env bash

# Copyright (c) 2020 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

run_test() {
    local arg
    echo
    echo ======================================================================
    for arg; do
        echo -n "$arg "
    done
    echo
    echo ======================================================================

    PYTHONPATH="$script_dir/../.." python -m "$@"
}

run_test "$@"
