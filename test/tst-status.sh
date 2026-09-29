test_run() {
    test_setup

    local users=(egor.tensin)

    local log_path
    log_path="$test_root_dir/status.log"
    local db_path
    db_path="$test_root_dir/status.csv"

    test_run_module vk.tracking.status \
        --log "$log_path" \
        --format csv \
        --output "$db_path" \
        "${users[@]}" &
    local pid="$!"

    sleep 3
    log "Log file: $log_path"
    log "Database file: $db_path"
    log "PID: $pid"

    local timeout=10
    log "Sleeping for $timeout seconds..."
    sleep "$timeout"

    log 'Terminating track_status.py...'
    kill "$pid"
    log 'Waiting for track_status.py to terminate...'
    wait "$pid" || true

    if [ ! -s "$log_path" ]; then
        fail "Log file '$log_path' either doesn't exists or is empty"
        return 1
    fi
    log 'Log file:'
    cat -- "$log_path" >&2

    if [ ! -s "$db_path" ]; then
        fail "Database file '$db_path' either doesn't exists or is empty"
        return 1
    fi
    log 'Database:'
    cat -- "$db_path" >&2
}
