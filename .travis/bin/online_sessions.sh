#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

readonly db_path="$script_dir/../share/test_db.csv"

try_output() {
    local output_path
    output_path="$( mktemp --dry-run )"

    local rm_aux_files
    rm_aux_files="$( printf -- 'rm -f -- %q' "$output_path" )"

    trap "$rm_aux_files" RETURN

    "$script_dir/../lib/test.sh" bin.online_sessions "$@" "$db_path" "$output_path"

    if file --brief --dereference --mime -- "$output_path" | grep --quiet -- 'charset=binary$'; then
        echo 'Output is a binary file, not going to show that'
        return 0
    fi

    echo "Output:"
    cat "$output_path"
}

online_sessions() {
    try_output --group-by user --output-format csv
    try_output --group-by user --output-format json

    try_output --group-by user --output-format plot
    try_output --group-by hour --output-format plot
    try_output --group-by date --output-format plot
    try_output --group-by weekday --output-format plot
}

fix_matplotlib() {
    # Get rid of:
    # tkinter.TclError: no display name and no $DISPLAY environment variable
    mkdir -p -- ~/.config/matplotlib
    echo 'backend: Agg' > ~/.config/matplotlib/matplotlibrc
}

main() {
    fix_matplotlib
    online_sessions
}

main
