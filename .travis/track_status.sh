#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

main() {
    local log_path
    log_path="$( mktemp )"

    nohup python3 -m bin.track_status egor.tensin > "$log_path" 2>&1 &
    local pid="$!"

    sleep 15
    kill -SIGINT "$pid"
    wait "$pid"

    cat "$log_path"
}

main
