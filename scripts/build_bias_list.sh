#!/usr/bin/env bash

set -e

GENEVA=${HOME}/storage/Geneva

main() {
    local output_filename=$1
    local date_to_use=$2

	grep "${date_to_use}" ${GENEVA}/logs/rsync.log |
    grep fits |
    grep -v autoguider |
    cut -d ' ' -f 5 |
    while read fname; do
        echo ${GENEVA}/${fname};
    done > ${output_filename}
}

main "$@"

