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

    plot_border = 0.02
    for (ledge, redge, axis) in zip(ledges, redges, axes):
        ind = (flux_mean >= ledge) & (flux_mean < redge)
        chosen_flux = corrected_flux[ind]
        chosen_fluxerr = fluxerr[ind]
        binned_lc = np.average(chosen_flux, axis=0,
                               weights=1. / chosen_fluxerr ** 2)
        binned_lc_err = np.sqrt(1. / np.sum(chosen_fluxerr ** -2., axis=0))
        axis.plot(tmid, binned_lc, '.', zorder=2)
        axis.errorbar(tmid, binned_lc, binned_lc_err, ls='None', alpha=0.2,
                      zorder=1, capsize=0.)

        med_binned = np.median(binned_lc)
        ylims = axis.get_ylim()
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
