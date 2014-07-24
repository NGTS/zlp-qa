#!/usr/bin/env bash

set -e

make_images() {
    local readonly rootdir=$(abspath $1)
    local readonly outputdir=$(abspath $2)

    if [[ -z "${TMPDIR}" ]]; then
        TMPDIR=/tmp
    fi

    EXT=png

    # extract overscan levels
    OUTPUTFILE="${outputdir}/00-overscan-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        find ${rootdir}/OriginalData/images -name 'IMAGE*.fits' > ${TMPDIR}/bias-frames.list
        python reduction/extract_overscan.py ${TMPDIR}/bias-frames.list -o ${TMPDIR}/extracted-bias-levels.csv
        python reduction/plot_overscan_levels.py ${TMPDIR}/extracted-bias-levels.csv -o ${OUTPUTFILE}
    else
        echo "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

main() {
    validate_arguments "$@"

    local readonly script_dir="$(dirname $(abspath $0))"
    echo "Running scripts from directory ${script_dir}"

    local readonly rootdir=$(abspath $1)
    local readonly outputdir=$(abspath $2)

    ensure_directory "${outputdir}"

    (cd ${script_dir} && make_images "${rootdir}" "${outputdir}")
}

ensure_directory() {
    test -d "$1" || mkdir -p "$1"
}

abspath() {
    readlink -f "$1"
}

validate_arguments() {
    if [[ "$#" != 2 ]]; then
        usage $0 >&2
        exit 1
    fi

    local readonly rootdir=$1
    local readonly outputdir=$2

    if [[ ! -d ${rootdir} ]]; then
        echo "Cannot find directory ${rootdir}" >&2
        exit 1
    fi
}

usage() {
    cat <<-EOF
Program usage: $0 <rootdir> <outputdir>
EOF
}

main "$@"
