# Copyright (c) 2020 Egor Tensin <egor@tensin.name>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts
# Distributed under the MIT License.

test_should_fail=
test_root_dir=

test_setup() {
    test_root_dir="$( mktemp -d )"

    log "Root directory: $test_root_dir"
}

test_cleanup_default() {
    if [ -n "$test_root_dir" ]; then
        log "Removing test's root directory: $test_root_dir"
        rm -rf -- "$test_root_dir"
    fi
}

test_run_module() {
    local cmd=(python -m "$@")
    log_run "${cmd[@]}"
    PYTHONPATH="$script_dir/.." "${cmd[@]}"
}
