#!/usr/bin/env bash

set -e

main() {
    local readonly rootdir=../zlp-script/testdata
    local readonly plotdir=/tmp/plots

    test -d ${plotdir} && rm -rf ${plotdir}

    bash ./run.sh ${rootdir} ${plotdir}
}

main
