#!/bin/bash

set -eu

find_files() {
    find ${NGTS}/flat-field-optimisation/data -name 'proc*.fits'
}

limit() {
    head -n 200
}

main() {
    find_files | limit > $1
}

main "$@"
