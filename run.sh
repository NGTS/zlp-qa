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

    # extract overscan levels
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-overscan-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        python reduction/extract_overscan.py \
            <(find -L ${rootdir}/OriginalData/images -name 'IMAGE*.fits*') -o - | \
            python reduction/plot_overscan_levels.py - -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

find_dark_frames() {
    find -L ${rootdir}/OriginalData/images -type d -name '*dark*' | xargs -I {} find -L {} -name 'IMAGE*.fits*'
}

plot_dark_levels() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-dark-levels.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
         python reduction/extract_dark_current.py <(find_dark_frames) -o - | python reduction/plot_dark_current.py - -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_dark_correlation() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-dark-correlation.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        python reduction/extract_dark_current.py <(find_dark_frames) -o - | \
            python reduction/plot_dark_current_correlation.py - -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_hist_equalised_master() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly frame_type="${3}"

    MASTERFILE=$(find ${rootdir}/Reduction/output -iname "*master${frame_type}*.fits" | head -n 1)
    if [[ ! -z "${MASTERFILE}" ]]; then
        OUTPUTSTUB="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-m${frame_type}"
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

    INFILE=$(find ${rootdir}/Reduction/output -name 'flat_total.fits' | head -n 1)
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-flat-total-adu.${EXT}"
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
    local readonly hdu="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-flux-vs-rms.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly fluxfile=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        if [[ -z ${fluxfile} ]]; then
            print_warning "No flux file found"
        else
            python photometry/flux_vs_rms.py ${fluxfile} --hdu ${hdu} -o ${OUTPUTFILE}
        fi
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_casu_flux_vs_rms() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-casu-flux-vs-rms.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly filename=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        python photometry/flux_vs_rms_with_casu.py ${filename} -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_rms_vs_time() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    local readonly hdu="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-rms-vs-time.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly filename=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        if [[ -z ${filename} ]]; then 
            print_warning "no photometry file found"
        else
            python photometry/rms_vs_time.py ${filename} -o ${OUTPUTFILE} --hdu ${hdu}
        fi
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_casu_rms_vs_time() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-casu-rms-vs-time.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly filename=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        python photometry/rms_vs_time_with_casu.py ${filename} -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_rms_with_binning() {
    local readonly rootdir="$1"
    local readonly plotsdir="${2}"
    local readonly hdu="$3"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-rms-with-binning.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly filename=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        if [[ -z ${TESTQA} ]]; then
            python photometry/multi_binning.py ${filename} -o ${OUTPUTFILE} --hdu ${hdu}
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

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-photometry-time-series.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        python photometry/plot_photometry_time_series.py ${presysrem} -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_binned_lightcurves_with_brightness() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-binned-lightcurves-by-brightness.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        local readonly presysrem=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        local readonly rawfiles=$(find -L ${rootdir}/Reduction/output -name 'proc*.phot' | sed 's/.phot$//')
        python photometry/binning_per_brightness.py ${presysrem} -o ${OUTPUTFILE} -r ${rawfiles}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_ag_stats() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-autoguider-results.${EXT}"
    if [[ ! -f "${OUTPUTFILE}" ]]; then
        local readonly resultfile=$(find -L ${rootdir}/AperturePhot/output -name 'output.fits')
        python astrometry/plot_ag_parameters.py "${resultfile}" -o "${OUTPUTFILE}"
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_extracted_astrometic_parameters() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-extracted-astrometric-parameters.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        python astrometry/extract_wcs_parameters.py <(find -L ${rootdir}/Reduction/output/ -name 'proc*.fits' | grep -v 'skybkg' | grep image) -o - | \
            python astrometry/plot_astrometric_parameters.py - -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi

}

plot_field_rotation() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-field-rotation.${EXT}"
    if [[ ! -f "${OUTPUTFILE}" ]]; then
        REDUCED_FILES_DIR="$(dirname $(find -L ${rootdir}/Reduction/output -name 'proc*.fits' | grep -v skybkg | grep image | head -n 1))"
        python external/field-rotation/run_on_files.py -o /dev/null ${REDUCED_FILES_DIR} -p ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_number_of_point_sources() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-number-of-point-sources.${EXT}"
    if [[ ! -f ${OUTPUTFILE} ]]; then
        python photometry/extract_npoint_sources.py <(find -L ${rootdir}/Reduction/output/ -name 'proc*.cat') -o - | \
            python photometry/plot_npoint_sources.py - -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
}

plot_psf_measurements() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    set +e
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-psf-measurements.${EXT}"
    PSFTEMPFILENAME=${TMPDIR}/psf_measurements.csv
    if [[ ! -f ${OUTPUTFILE} ]]; then
        if [ ! -f ${PSFTEMPFILENAME} ]; then
            python photometry/extract_psf_measurements.py <(find -L ${rootdir}/Reduction/output/ -name 'proc*.phot') -o ${PSFTEMPFILENAME}
        fi
        python photometry/plot_psf_measurements.py ${PSFTEMPFILENAME} -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
    set -e
}

plot_psf_ratios() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    set +e
    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-psf-ratios.${EXT}"
    PSFTEMPFILENAME=${TMPDIR}/psf_measurements.csv
    if [[ ! -f ${OUTPUTFILE} ]]; then
        if [ ! -f ${PSFTEMPFILENAME} ]; then
            python photometry/extract_psf_measurements.py <(find -L ${rootdir}/Reduction/output/ -name 'proc*.phot') -o ${PSFTEMPFILENAME}
        fi
        python photometry/plot_psf_ratios.py ${PSFTEMPFILENAME} -o ${OUTPUTFILE}
    else
        print_status "Output file ${OUTPUTFILE} exists, skipping"
    fi
    set -e
}

plot_pixel_centre_of_mass() {
    local readonly rootdir="$1"
    local readonly plotsdir="$2"

    OUTPUTFILE="${plotsdir}/$(compute_plot_number ${PLOTCOUNTER})-pixel-centre-of-mass.${EXT}"
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

    PLOTCOUNTER="1"

    set +e
    run_then_inc_plot_counter plot_overscan_levels "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_dark_levels "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_dark_correlation "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_hist_equalised_master "${rootdir}" "${plotsdir}" "bias"
    run_then_inc_plot_counter plot_hist_equalised_master "${rootdir}" "${plotsdir}" "dark"
    run_then_inc_plot_counter plot_hist_equalised_master "${rootdir}" "${plotsdir}" "flat"
    run_then_inc_plot_counter plot_total_flat_adu "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_flux_vs_rms "${rootdir}" "${plotsdir}" flux
    run_then_inc_plot_counter plot_flux_vs_rms "${rootdir}" "${plotsdir}" tamflux
    run_then_inc_plot_counter plot_flux_vs_rms "${rootdir}" "${plotsdir}" casudet
    run_then_inc_plot_counter plot_casu_flux_vs_rms "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_rms_vs_time "${rootdir}" "${plotsdir}" flux
    run_then_inc_plot_counter plot_rms_vs_time "${rootdir}" "${plotsdir}" tamflux
    run_then_inc_plot_counter plot_rms_vs_time "${rootdir}" "${plotsdir}" casudet
    run_then_inc_plot_counter plot_casu_rms_vs_time "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_rms_with_binning "${rootdir}" "${plotsdir}" flux
    run_then_inc_plot_counter plot_rms_with_binning "${rootdir}" "${plotsdir}" tamflux
    run_then_inc_plot_counter plot_rms_with_binning "${rootdir}" "${plotsdir}" casudet
    run_then_inc_plot_counter plot_photometric_time_series "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_number_of_point_sources "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_psf_measurements "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_psf_ratios "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_binned_lightcurves_with_brightness "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_ag_stats "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_extracted_astrometic_parameters "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_field_rotation "${rootdir}" "${plotsdir}"
    run_then_inc_plot_counter plot_pixel_centre_of_mass "${rootdir}" "${plotsdir}"

    make_astrometric_summary "${rootdir}" "${plotsdir}"
    make_psf_summary "${rootdir}" "${plotsdir}"
    make_psf_residuals_summary "${rootdir}" "${plotsdir}"
    set -e

    make_html "${outputdir}"
}

compute_plot_number() {
    local readonly number="$1"
    printf "%02d" "${number}"
}

# Keep the plot counter incrementing
run_then_inc_plot_counter() {
    $*
    ((PLOTCOUNTER++))
}

make_astrometric_summary() {
    local readonly rootdir="${1}"
    local readonly plotsdir="${2}"
    python scripts/copy_pngs.py <(find -L ${rootdir}/Reduction/output -name '*.png' | \
        grep -v psf | \
        grep -v model | \
        grep -v residuals) -o ${plotsdir} --stub vector-astrometry --plot-index-offset 70
}

make_psf_summary() {
    local readonly rootdir="${1}"
    local readonly plotsdir="${2}"
    python scripts/copy_pngs.py <(find -L ${rootdir}/Reduction/output -name '*.png' | grep psf) -o ${plotsdir} --stub psf --plot-index-offset 80
}

make_psf_residuals_summary() {
    local readonly rootdir="${1}"
    local readonly plotsdir="${2}"
    python scripts/copy_pngs.py <(find -L ${rootdir}/Reduction/output -name '*.png' | grep residuals) -o ${plotsdir} --stub psf-residuals --plot-index-offset 90
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
    if [[ -z ${DISABLE_ANACONDA} ]]; then
        if [[ -d ${HOME}/anaconda ]]; then
            export PATH=${HOME}/anaconda/bin:${PATH}
        fi
    fi
    export PYTHONPATH=$(abspath $0):$PYTHONPATH
    echo "Using python: $(which python)"
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
