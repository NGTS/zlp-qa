#!/usr/bin/env bash

set -e

main() {
    local readonly rootdir=../zlp-script/testdata
    local readonly plotdir=plots

    test -d ${plotdir} && rm -rf ${plotdir}

    TESTQA=true bash ./run.sh ${rootdir} ${plotdir}
}

main
