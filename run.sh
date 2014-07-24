#!/usr/bin/env bash

set -e

main() {
    validate_arguments "$@"

    local readonly script_dir="$(dirname $(readlink -f $0))"
    echo "Running scripts from directory ${script_dir}"

    local readonly rootdir=$1
    local readonly outputdir=$2

    make ROOTDIR="${rootdir}" PLOTSDIR="${outputdir}"
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
