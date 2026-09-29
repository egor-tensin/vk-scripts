test_run() {
    test_setup

    local users=(egor.tensin kreed58)
    local db_path
    db_path="$test_root_dir/db.csv"

    test_run_module vk.tracking.status --only-once -o "$db_path" "${users[@]}"

    if [ ! -s "$db_path" ]; then
        fail "Database file '$db_path' either doesn't exists or is empty"
        return 1
    fi

    log "Database:"
    cat -- "$db_path" >&2

    local lines
    lines="$( cat -- "$db_path" | wc -l )"

    if [ "$lines" -ne 2 ]; then
        fail "Database '$db_path' has the wrong number of entries"
        return 1
    fi
}
