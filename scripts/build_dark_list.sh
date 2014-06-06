#!/usr/bin/env bash

set -e

GENEVA=${HOME}/storage/Geneva

main() {
	grep '2014\/06\/06' ${GENEVA}/logs/rsync.log |
    grep fits |
    grep dark |
    grep -v autoguider |
    cut -d ' ' -f 5 |
    while read fname; do
        echo ${GENEVA}/${fname};
    done > $1
}

main "$@"

