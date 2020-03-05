#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

test_users() {
    local log_path
    log_path="$( mktemp )"
    local db_path
    db_path="$( mktemp --dry-run )"

    local rm_aux_files
    rm_aux_files="$( printf -- 'rm -f -- %q %q' "$log_path" "$db_path" )"
    trap "$rm_aux_files" RETURN

    ./.travis/test.sh bin.track_status "$@" --log "$log_path" --format csv --output "$db_path" &
    local pid="$!"

    sleep 3
    echo "Log file path: $log_path"
    echo "DB file path: $db_path"
    echo "PID: $pid"

    local timeout=10
    echo "Sleeping for $timeout seconds..."
    sleep "$timeout"

    echo 'Terminating track_status.py...'
    kill "$pid"
    echo 'Waiting for track_status.py to terminate...'
    wait "$pid" || true

    echo "Log file:"
    cat "$log_path"
    echo "DB:"
    cat "$db_path"
}

main() {
    test_users egor.tensin
}

main "$@"
