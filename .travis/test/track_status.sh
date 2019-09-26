#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

track_status() {
    local log_path
    log_path="$( mktemp )"
    echo "Log file path: $log_path"

    local db_path
    db_path="$( mktemp --dry-run )"
    echo "DB file path: $db_path"

    local rm_aux_files
    rm_aux_files="$( printf -- 'rm -f -- %q %q' "$log_path" "$db_path" )"

    trap "$rm_aux_files" RETURN

    echo 'Running track_status.py...'
    python3 -m bin.track_status "$@" --log "$log_path" --format csv --output "$db_path" &
    local pid="$!"
    echo "Its PID is $pid"

    local timeout=15
    echo "Sleeping for $timeout seconds..."
    sleep "$timeout"

    echo 'Terminating track_status.py...'
    kill -SIGINT "$pid"
    echo 'Waiting for track_status.py to terminate...'
    wait "$pid"

    echo "Log file:"
    cat "$log_path"
    echo "DB:"
    cat "$db_path"
}

main() {
    track_status egor.tensin
}

main "$@"
