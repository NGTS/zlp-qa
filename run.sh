#!/usr/bin/env bash

set -e

make_images() {
    local readonly rootdir=$(abspath $1)
    local readonly outputdir=$(abspath $2)
    local readonly plotsdir="${outputdir}/plots"

    ensure_directory "${plotsdir}"


    if [[ -z "${TMPDIR}" ]]; then
        TMPDIR=/tmp
    fi

    EXT=png

    # extract overscan levels
    OUTPUTFILE="${plotsdir}/00-overscan-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        find ${rootdir}/OriginalData/images -name 'IMAGE*.fits' > ${TMPDIR}/bias-frames.list
        python reduction/extract_overscan.py ${TMPDIR}/bias-frames.list -o ${TMPDIR}/extracted-bias-levels.csv
        python reduction/plot_overscan_levels.py ${TMPDIR}/extracted-bias-levels.csv -o ${OUTPUTFILE}
    else
        echo "Output file ${OUTPUTFILE} exists, skipping"
    fi

    OUTPUTFILE="${plotsdir}/01-dark-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        find ${rootdir}/OriginalData/images -type d -name '*dark*' | xargs -I {} find {} -name 'IMAGE*.fits' > ${TMPDIR}/dark-frames.list
        python reduction/extract_dark_current.py ${TMPDIR}/dark-frames.list -o ${TMPDIR}/extracted-dark-levels.csv
        python reduction/plot_dark_current.py ${TMPDIR}/extracted-dark-levels.csv -o ${OUTPUTFILE}
    else
        echo "Output file ${OUTPUTFILE} exists, skipping"
    fi

    OUTPUTFILE="${plotsdir}/02-dark-correlation.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        python reduction/plot_dark_current_correlation.py ${TMPDIR}/extracted-dark-levels.csv -o ${OUTPUTFILE}
    else
        echo "Output file ${OUTPUTFILE} exists, skipping"
    fi

    OUTPUTFILE="${plotsdir}/04-flux-vs-rms.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find ${rootdir}/AperturePhot/output -name 'output.fits')
        local readonly postsysrem=$(find ${rootdir}/AperturePhot/output -name 'tamout.fits')
        if [[ -z ${postsysrem} ]]; then
            echo "No post-sysrem file found"
            python photometry/flux_vs_rms.py --pre-sysrem ${presysrem} -o ${OUTPUTFILE}
        else
            python photometry/flux_vs_rms.py --pre-sysrem ${presysrem} --post-sysrem ${postsysrem} -o ${OUTPUTFILE}
        fi
    else
        echo "Output file ${OUTPUTFILE} exists, skipping"
    fi

    OUTPUTFILE="${plotsdir}/05-rms-vs-time.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find ${rootdir}/AperturePhot/output -name 'output.fits')
        local readonly postsysrem=$(find ${rootdir}/AperturePhot/output -name 'tamout.fits')
        if [[ -z ${postsysrem} ]]; then 
            echo "No post-sysrem file found"
            python photometry/rms_vs_time.py --pre-sysrem ${presysrem} -o ${OUTPUTFILE}
        else
            python photometry/rms_vs_time.py --pre-sysrem ${presysrem} --post-sysrem ${postsysrem} -o ${OUTPUTFILE}
        fi
    else
        echo "Output file ${OUTPUTFILE} exists, skipping"
    fi

    make_html "${outputdir}"
}

make_html() {
    local readonly outputdir="$1"
    python view/build_html.py ${outputdir} -o ${outputdir}/index.html --extension ${EXT}
}

ensure_stilts() {
    test -f astrometry/stilts.jar || curl -L http://www.star.bris.ac.uk/~mbt/stilts/stilts.jar > astrometry/stilts.jar
}

main() {
    validate_arguments "$@"
    ensure_stilts

    local readonly script_dir="$(dirname $(abspath $0))"
    echo "Running scripts from directory ${script_dir}"

    local readonly rootdir=$(abspath $1)
    local readonly outputdir=$(abspath $2)

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
