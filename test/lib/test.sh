# Copyright (c) 2020 Egor Tensin <egor@tensin.name>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts
# Distributed under the MIT License.

test_run_module() {
    local cmd=(python3 -m "$@")
    log_run "${cmd[@]}"
    PYTHONPATH="$tests_dir/.." "${cmd[@]}"
}
