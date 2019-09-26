#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

readonly db_path='.travis/test_db.csv'

_online_sessions() {
    local output_path
    output_path="$( mktemp --dry-run )"

    local rm_aux_files
    rm_aux_files="$( printf -- 'rm -f -- %q' "$output_path" )"

    trap "$rm_aux_files" RETURN

    echo "Running online_sessions.py..."
    python3 -m bin.online_sessions "$@" "$db_path" "$output_path"

    if file --brief --dereference --mime -- "$output_path" | grep --quiet -- 'charset=binary$'; then
        echo 'Output is a binary file, not going to show that'
        return 0
    fi

    echo "Output:"
    cat "$output_path"
}

online_sessions() {
    # Get rid of:
    # tkinter.TclError: no display name and no $DISPLAY environment variable
    mkdir -p -- ~/.config/matplotlib
    echo 'backend: Agg' > ~/.config/matplotlib/matplotlibrc

    _online_sessions --group-by user --output-format csv
    _online_sessions --group-by user --output-format json

    _online_sessions --group-by user --output-format plot
    _online_sessions --group-by hour --output-format plot
    _online_sessions --group-by date --output-format plot
    _online_sessions --group-by weekday --output-format plot
}

main() {
    online_sessions
}

main "$@"
