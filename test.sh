#!/usr/bin/env bash

set -e

export TMPDIR=${PWD}/tmp

cleanup_temp_files() {
    find "${TMPDIR}" -type f -not -name '.gitkeep' -delete
}

main() {
    local readonly rootdir=../zlp-script/testdata
    local readonly plotdir=plots

    test -d ${plotdir} && rm -rf ${plotdir}
    cleanup_temp_files

    DISABLE_ANACONDA=true TESTQA=true bash ./run.sh ${rootdir} ${plotdir} 2>&1 | tee test.log
}

main
