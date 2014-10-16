#!/usr/bin/env bash

set -e

print_status() {
    echo "$@" >&2
}

print_warning() {
    print_status "*** WARNING: $@"
}

[[ ${TESTQA} ]] && print_status "Testing"

if [[ -z "${TMPDIR}" ]]; then
    TMPDIR=/tmp
fi

EXT=png

plot_overscan_levels() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    # extract overscan levels
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-overscan-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        find -L ${rootdir}/OriginalData/images -name 'IMAGE*.fits' > ${TMPDIR}/bias-frames.list
        python reduction/extract_overscan.py ${TMPDIR}/bias-frames.list -o ${TMPDIR}/extracted-bias-levels.csv
        python reduction/plot_overscan_levels.py ${TMPDIR}/extracted-bias-levels.csv -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_dark_levels() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-dark-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        find -L ${rootdir}/OriginalData/images -type d -name '*dark*' | xargs -I {} find -L {} -name 'IMAGE*.fits' > ${TMPDIR}/dark-frames.list
        python reduction/extract_dark_current.py ${TMPDIR}/dark-frames.list -o ${TMPDIR}/extracted-dark-levels.csv
        python reduction/plot_dark_current.py ${TMPDIR}/extracted-dark-levels.csv -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_dark_correlation() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-dark-correlation.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        python reduction/plot_dark_current_correlation.py ${TMPDIR}/extracted-dark-levels.csv -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_hist_equalised_master() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly frame_type="${3}"
    local readonly plot_number="$4"

    MASTERFILE=$(find ${rootdir}/Reduction/output -iname "*master${frame_type}*.fits" | head -n 1)
    if [[ ! -z "${MASTERFILE}" ]]; then
        OUTPUTSTUB="${plotsdir}/$(compute_plot_number ${plot_number})-m${frame_type}"
        OUTPUTFILE="${OUTPUTSTUB}.png"
        if [[ ! -f "${OUTPUTFILE}" ]]; then
            python scripts/plot_hist_equalised.py ${MASTERFILE} --stub ${OUTPUTSTUB} --ext ${EXT}
        else
            print_status "Output file ${OUTPUTFILE} exists, skipping"
        fi
    else
        print_warning "Cannot find master ${frame_type} file"
    fi
}

plot_total_flat_adu() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    INFILE=$(find ${rootdir}/Reduction/output -name 'flat_total.fits' | head -n 1)
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-flat-total-adu.${EXT}"
    if [[ ! -z "${INFILE}" ]]; then
        if [[ ! -f "${OUTPUTFILE}" ]]; then
            python reduction/plot_total_flat_adu.py "${INFILE}" -o "${OUTPUTFILE}"
        else
            print_status "Output file ${OUTPUTFILE} exists, skipping"
        fi
    else
        print_warning "Cannot find flat totals file flat_total.fits"
    fi
}

plot_flux_vs_rms() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-flux-vs-rms.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        local readonly postsysrem=$(find -L ${rootdir}/AperturePhot/output -name 'tamout.fits')
        if [[ -z ${postsysrem} ]]; then
            print_warning "No post-sysrem file found"
            python photometry/flux_vs_rms.py --pre-sysrem ${presysrem} -o ${OUTPUTFILE}
        else
            python photometry/flux_vs_rms.py --pre-sysrem ${presysrem} --post-sysrem ${postsysrem} -o ${OUTPUTFILE}
        fi
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_rms_vs_time() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-rms-vs-time.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        local readonly postsysrem=$(find -L ${rootdir}/AperturePhot/output -name 'tamout.fits')
        if [[ -z ${postsysrem} ]]; then 
            print_warning "No post-sysrem file found"
            python photometry/rms_vs_time.py --pre-sysrem ${presysrem} -o ${OUTPUTFILE}
        else
            python photometry/rms_vs_time.py --pre-sysrem ${presysrem} --post-sysrem ${postsysrem} -o ${OUTPUTFILE}
        fi
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_rms_with_binning() {
    local readonly rootdir="$1"
    local readonly plotsdir="${2}"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-rms-with-binning.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        if [[ -z ${TESTQA} ]]; then
            python photometry/multi_binning.py ${presysrem} -o ${OUTPUTFILE}
        else
            print_status "RMS with binning test disabled; it does not work with this data set"
        fi
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_photometric_time_series() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-photometry-time-series.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        python photometry/plot_photometry_time_series.py ${presysrem} -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_extracted_astrometic_parameters() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-extracted-astrometric-parameters.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        find -L ${rootdir}/Reduction/output/ -name 'proc*.fits' | grep -v 'skybkg' | grep image > ${TMPDIR}/science-images-list.txt
        python astrometry/extract_wcs_parameters.py ${TMPDIR}/science-images-list.txt -o ${TMPDIR}/astrometric-extraction.csv
        python astrometry/plot_astrometric_parameters.py ${TMPDIR}/astrometric-extraction.csv -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_pixel_centre_of_mass() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly plot_number="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${plot_number})-pixel-centre-of-mass.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly filename=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        python photometry/pixel-com.py "${filename}" -o "${OUTPUTFILE}"
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

make_images() {
    local readonly rootdir=$(abspath $1)
    local readonly outputdir=$(abspath $2)
    local readonly plotsdir="${outputdir}/plots"

    ensure_directory "${plotsdir}"

    plot_overscan_levels "${rootdir}" "${plotsdir}" 0
    plot_dark_levels "${rootdir}" "${plotsdir}" 1
    plot_dark_correlation "${rootdir}" "${plotsdir}" 2
    plot_hist_equalised_master "${rootdir}" "${plotsdir}" "bias" 3
    plot_hist_equalised_master "${rootdir}" "${plotsdir}" "dark" 4
    plot_hist_equalised_master "${rootdir}" "${plotsdir}" "flat" 5
    plot_total_flat_adu "${rootdir}" "${plotsdir}" 6
    plot_flux_vs_rms "${rootdir}" "${plotsdir}" 7
    plot_rms_vs_time "${rootdir}" "${plotsdir}" 8
    plot_rms_with_binning "${rootdir}" "${plotsdir}" 9
    plot_photometric_time_series "${rootdir}" "${plotsdir}" 10
    plot_extracted_astrometic_parameters "${rootdir}" "${plotsdir}"  12
    plot_pixel_centre_of_mass "${rootdir}" "${plotsdir}" 13

    make_astrometric_summary "${rootdir}" "${plotsdir}"
    make_psf_summary "${rootdir}" "${plotsdir}"

    make_html "${outputdir}"
}

compute_plot_number() {
    local readonly number="$1"
    printf "%02d" "${number}"
}

make_astrometric_summary() {
    local readonly rootdir="${1}"
    local readonly plotsdir="${2}"

    local readonly imglist=${TMPDIR}/astrometric-pngs.txt

    find -L ${rootdir}/Reduction/output -name '*.png' | grep -v psf > ${imglist}
    python scripts/copy_pngs.py ${imglist} -o ${plotsdir} --stub vector-astrometry --offset 80
}

make_psf_summary() {
    local readonly rootdir="${1}"
    local readonly plotsdir="${2}"

    local readonly imglist=${TMPDIR}/psf-pngs.txt

    find -L ${rootdir}/Reduction/output -name '*.png' | grep psf > ${imglist}
    python scripts/copy_pngs.py ${imglist} -o ${plotsdir} --stub psf --offset 90
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
    setup_environment
    # ensure_stilts
    print_status "Starting QA"
    print_status $(printf '%80s\n' | tr ' ' -)

    local readonly script_dir="$(dirname $(abspath $0))"
    print_status "Running scripts from directory ${script_dir}"

    local readonly rootdir=$(abspath $1)
    local readonly outputdir=$(abspath $2)

    (cd ${script_dir} && make_images "${rootdir}" "${outputdir}")
}

ensure_directory() {
    test -d "$1" || mkdir -p "$1"
}

abspath() {
    python -c "import os; print os.path.realpath('${1}')"
}


validate_arguments() {
    if [[ "$#" != 2 ]]; then
        usage $0 >&2
        exit 1
    fi

    local readonly rootdir=$1
    local readonly outputdir=$2

    if [[ ! -d ${rootdir} ]]; then
        print_warning "Cannot find directory ${rootdir}" >&2
        exit 1
    fi
}

setup_environment() {
    if [[ -d ${HOME}/anaconda ]]; then
        export PATH=${HOME}/anaconda/bin:${PATH}
    fi

    export PYTHONPATH=$(abspath $0):$PYTHONPATH
}

usage() {
    cat <<-EOF
Program usage: $0 <rootdir> <outputdir>
EOF
}

is_main() {
    [[ "${BASH_SOURCE[0]}" == "$0" ]]
}

if is_main; then
    main "$@"
fi
