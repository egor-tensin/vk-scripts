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

dump() {
    local msg
    for msg; do
        echo "$script_name: $msg"
    done
}

test_users() {
    local log_path
    log_path="$( mktemp )"
    local db_path
    db_path="$( mktemp --dry-run )"

    local rm_aux_files
    rm_aux_files="$( printf -- 'rm -f -- %q %q' "$log_path" "$db_path" )"
    trap "$rm_aux_files" RETURN

    "$script_dir/../lib/test.sh" vk.tracking.status "$@" --log "$log_path" --format csv --output "$db_path" &
    local pid="$!"

    sleep 3
    dump "Log file path: $log_path"
    dump "DB file path: $db_path"
    dump "PID: $pid"

    local timeout=10
    dump "Sleeping for $timeout seconds..."
    sleep "$timeout"

    dump 'Terminating track_status.py...'
    kill "$pid"
    dump 'Waiting for track_status.py to terminate...'
    wait "$pid" || true

    dump "Log file:"
    cat "$log_path"
    dump "DB:"
    cat "$db_path"
}

main() {
    test_users egor.tensin
}

main "$@"
