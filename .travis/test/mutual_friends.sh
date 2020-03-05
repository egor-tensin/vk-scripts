#!/usr/bin/env bash

# Copyright (c) 2019 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

test_users() {
    ./.travis/test.sh bin.mutual_friends --format csv "$@"
    ./.travis/test.sh bin.mutual_friends --format json "$@"
}

main() {
    test_users kreed58 maxkorzh_official
}

main "$@"
