test_db_path="$script_dir/data/test_db.csv"
readonly test_db_path

_test_format() {
    local output_path
    output_path="$( mktemp --tmpdir="$test_root_dir" )"

    test_run_module vk.tracking.sessions "$@" "$test_db_path" "$output_path"

    if [ ! -s "$output_path" ]; then
        fail "Output file '$output_path' either doesn't exists or is empty"
        return 1
    fi

    if file --brief --dereference --mime -- "$output_path" | grep --quiet -- 'charset=binary$'; then
        log 'Output is a binary file, not going to show that'
        return 0
    fi

    cat -- "$output_path" >&2
}

_test_group_by() {
    local group_by
    for group_by; do
        local format
        for format in csv json plot; do
            _test_format --output-format "$format" --group-by "$group_by"
        done
    done
}

_test_main() {
    _test_group_by user
    _test_group_by hour
    _test_group_by date
    _test_group_by weekday
}

test_run() {
    test_setup
    _test_main
}
