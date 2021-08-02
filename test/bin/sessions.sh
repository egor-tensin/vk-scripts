#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir
script_name="$( basename -- "${BASH_SOURCE[0]}" )"
readonly script_name

readonly db_path="$script_dir/../share/test_db.csv"

dump() {
    local msg
    for msg; do
        echo "$script_name: $msg"
    done
}

test_output() {
    local output_path
    output_path="$( mktemp --dry-run )"

    local rm_aux_files
    rm_aux_files="$( printf -- 'rm -f -- %q' "$output_path" )"

    trap "$rm_aux_files" RETURN

    "$script_dir/../lib/test.sh" vk.tracking.sessions "$@" "$db_path" "$output_path"

    if file --brief --dereference --mime -- "$output_path" | grep --quiet -- 'charset=binary$'; then
        dump 'Output is a binary file, not going to show that'
        return 0
    fi

    cat "$output_path"
}

group_by() {
    test_output --output-format csv  --group-by "$@"
    test_output --output-format json --group-by "$@"
    test_output --output-format plot --group-by "$@"
}

online_sessions() {
    group_by user
    group_by hour
    group_by date
    group_by weekday
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
