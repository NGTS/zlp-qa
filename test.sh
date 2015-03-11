#!/usr/bin/env bash

set -e

cleanup_temp_files() {
    if [ -z "${TMPDIR}" ]; then
        TMPDIR=/tmp
    fi

    for fname in bias-frames.list dark-frames.list science-images-list.txt astrometric-pngs.txt psf-pngs.txt
    do
        fullpath="${TMPDIR}/${fname}"
        test -f "${fullpath}" && rm "${fullpath}" || true
    done
}

main() {
    local readonly rootdir=../zlp-script/testdata
    local readonly plotdir=plots

    test -d ${plotdir} && rm -rf ${plotdir}
    cleanup_temp_files

    TESTQA=true bash ./run.sh ${rootdir} ${plotdir} 2>&1 | tee test.log
}

main
