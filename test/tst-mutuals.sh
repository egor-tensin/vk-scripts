test_run() {
    test_setup

    local users=(kreed58 korya_mc)

    test_run_module vk.mutuals --format csv "${users[@]}"  > "$test_root_dir/mutuals.csv"
    test_run_module vk.mutuals --format json "${users[@]}" > "$test_root_dir/mutuals.json"

    local expected=10

    local actual_csv
    actual_csv="$( cat -- "$test_root_dir/mutuals.csv" | wc -l )"
    log "Mutuals in CSV: $actual_csv"

    if [ "$actual_csv" -lt "$expected" ]; then
        fail "Expected a lot more mutual friends in CSV output"
        fail_details "Expected: $expected"
        fail_details "Actual: $actual_csv"
        return 1
    fi

    local actual_json
    actual_json="$( grep -F -- '"id":' "$test_root_dir/mutuals.json" | wc -l )"
    log "Mutuals in JSON: $actual_json"

    if [ "$actual_json" -lt "$expected" ]; then
        fail "Expected a lot more mutual friends in JSON output"
        fail_details "Expected: $expected"
        fail_details "Actual: $actual_json"
        return 1
    fi

    if [ "$actual_csv" -ne "$actual_json" ]; then
        fail "Number of mutuals in CSV unequal to that in JSON"
        fail_details "Can technically happen, because it's kind of a race"
        return 1
    fi
}
