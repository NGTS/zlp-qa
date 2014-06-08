#!/bin/bash

set -eu

main() {
    find ${NGTS}/ZLP/wcsfit-stacking-residuals/data -name 'proc*.fits' | tail -n 50 > $1
}

main "$@"
