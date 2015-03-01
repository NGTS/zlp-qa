#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import


import argparse
import fitsio
import numpy as np
import os
from qa_common import get_logger
from qa_common.plotting import plt
from qa_common.airmass_correct import remove_extinction
from qa_common.filter_objects import good_measurement_indices_from_fits
from qa_common.photometry import build_bins


logger = get_logger(__file__)

METADATA_KEYS = ['mjd', 'airmass', 'chstemp']
PLOT_KEYS = ['airmass', 'chstemp', 'median_count_rate']
MJD0 = None


def _extract_metadata(fname):
    header = fitsio.read_header(fname)
    data = fitsio.read(fname)
    initial = {key: header[key] for key in METADATA_KEYS}
    initial.update({'median_count_rate': np.median(data) / header['exposure']})
    return initial


def extract_metadata(rawfiles):
    values = map(_extract_metadata, rawfiles)
    return sorted(values, key=lambda row: row['mjd'])


def humanise_key(key):
    return key.replace('_', ' ').capitalize()


def plot_metadata_series(axis, metadata, key, x=None, *args, **kwargs):
    y = np.array([row[key] for row in metadata])
    x = x if x is not None else np.array([row['mjd'] for row in metadata]) - MJD0
    axis.plot(x, y, label=humanise_key(key), *args, **kwargs)
    axis.legend(loc='best')


def main(args):
    global MJD0
    ledges, redges = build_bins()

    assert all(os.path.isfile(f) for f in args.reduced_files)
    metadata = extract_metadata(args.reduced_files)

    logger.info('Reading data from %s', args.filename)
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
    logger.info('Found %s exposure times: %s', len(unique_exposure_times),
                unique_exposure_times)

    logger.info('Normalising by exposure time')
    flux /= exposure
    fluxerr /= exposure
    logger.info('Removing extinction')
    corrected_flux = remove_extinction(flux, airmass,
                                       flux_min=ledges[2],
                                       flux_max=ledges[5])

    MJD0 = int(tmid.min())
    tmid -= MJD0

    flux_mean = np.average(corrected_flux, axis=1, weights=1. / fluxerr ** 2)

    fig, axes = plt.subplots(len(ledges) + len(PLOT_KEYS), 1, sharex=True,
                             figsize=(8, 15))

    colours = ['r', 'g', 'b', 'c', 'm', 'k', 'y']
    plot_border = 0.02
    for (ledge, redge, axis) in zip(ledges, redges, axes[len(PLOT_KEYS):]):
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

    for (key, axis) in zip(PLOT_KEYS, axes):
        plot_metadata_series(axis, metadata, key, ls='None', marker='.')

    axes[-1].set_xlabel(r'MJD - {}'.format(MJD0))

    fig.tight_layout()

    if args.output is not None:
        logger.info('Rendering to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=False,
            type=argparse.FileType(mode='w'))
    parser.add_argument('-r', '--reduced-files', nargs='+')
    main(parser.parse_args())
