#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import


import argparse
import fitsio
import numpy as np
from qa_common import plt, get_logger
from qa_common.airmass_correct import remove_extinction
from qa_common.filter_objects import good_measurement_indices_from_fits
from qa_common.photometry import build_bins


logger = get_logger(__file__)


def main(args):
    ledges, redges = build_bins()

    logger.info('Reading data', filename=args.filename)
    with fitsio.FITS(args.filename) as infile:
        per_object_ind, per_image_ind = good_measurement_indices_from_fits(
            infile)

        flux = infile['flux'].read()[per_object_ind][:, per_image_ind]
        fluxerr = infile['fluxerr'].read()[per_object_ind][:, per_image_ind]
        imagelist = infile['imagelist']
        airmass = imagelist['airmass'].read()[per_image_ind]
        exposure = imagelist['exposure'].read()[per_image_ind]
        tmid = imagelist['tmid'].read()[per_image_ind]

    unique_exposure_times = sorted(list(set(exposure)))
    logger.info('Found exposure times', number=len(unique_exposure_times),
                data=unique_exposure_times)

    logger.info('Normalising by exposure time')
    flux /= exposure
    fluxerr /= exposure
    logger.info('Removing extinction')
    corrected_flux = remove_extinction(flux, airmass,
                                       flux_min=ledges[2],
                                       flux_max=ledges[5])

    tmid0 = int(tmid.min())
    tmid -= tmid0

    flux_mean = np.average(corrected_flux, axis=1, weights=1. / fluxerr ** 2)

    fig, axes = plt.subplots(len(ledges), 1, sharex=True)

    colours = ['r', 'g', 'b', 'c', 'm', 'k', 'y']
    plot_border = 0.02
    for (ledge, redge, axis) in zip(ledges, redges, axes):
        for exptime, colour in zip(unique_exposure_times, colours):
            ind = (flux_mean >= ledge) & (flux_mean < redge)
            exptime_ind = exposure == exptime
            chosen_flux = corrected_flux[ind][:, exptime_ind]

            chosen_fluxerr = fluxerr[ind][:, exptime_ind]
            binned_lc = np.average(chosen_flux, axis=0,
                                weights=1. / chosen_fluxerr ** 2)
            binned_lc_err = np.sqrt(1. / np.sum(chosen_fluxerr ** -2., axis=0))
            axis.plot(tmid[exptime_ind], binned_lc, '.', zorder=2,
                      color=colour)

        axis.yaxis.set_major_locator(plt.MaxNLocator(5))
        axis.set_xlim(tmid.min() - 0.005,
                      tmid.max() + 0.005)

    axes[-1].set_xlabel(r'MJD - {}'.format(tmid0))

    fig.tight_layout()
    logger.info('Rendering', filename=args.output)
    plt.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=True)
    main(parser.parse_args())
