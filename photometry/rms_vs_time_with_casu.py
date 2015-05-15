#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
from qa_common.plotting import plt, subplots
from qa_common.qa_logging import get_logger
import numpy as np
from astropy.io import fits

logger = get_logger(__file__)


def compute_stats(data):
    return np.percentile(data, [16, 50, 84], axis=0)


def errorbar(ax, x, y, e, *args, **kwargs):
    ax.errorbar(x, y, e,
                ls='None',
                marker='None',
                capsize=0.,
                alpha=0.3,
                lw=1., *args, **kwargs)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    with fits.open(args.filename) as infile:
        imagelist = infile['imagelist'].data
        imag = -2.5 * np.log10(infile['flux'].data)
        detflux = infile['casudet'].data

    mjd = imagelist['tmid']
    mjd0 = int(mjd.min())
    mjd -= mjd0
    normalised_flux = detflux - np.median(detflux, axis=1)[:, np.newaxis]
    normalised_raw = imag - np.median(imag, axis=1)[:, np.newaxis]

    with subplots() as (fig, axes):

        l, med, u = compute_stats(normalised_flux)
        err = (u - l) / np.sqrt(normalised_flux.shape[0])
        errorbar(axes[0], mjd, med, err, zorder=10)
        axes[0].plot(mjd, med, '.r', zorder=11)
        ylims = axes[0].get_ylim()

        med_detrended = np.median(med)
        axes[0].axhline(med_detrended, color='k', ls='--', zorder=50)
        axes[0].axhline(med_detrended + 1E-3, color='k', ls=':', zorder=50)
        axes[0].axhline(med_detrended - 1E-3, color='k', ls=':', zorder=50)

        l, med, u = compute_stats(normalised_raw)
        err = (u - l) / np.sqrt(normalised_raw.shape[0])
        errorbar(axes[0], mjd, med, err, zorder=5)
        axes[0].plot(mjd, med, '.k', zorder=6)
        axes[0].set_ylim(*ylims)

        for ax in axes:
            ax.invert_yaxis()

        axes[0].set_ylabel(r'Raw')
        axes[0].set_ylabel(r'Post-CASU')
        axes[-1].set_xlabel(r'MJD - {}'.format(mjd0))

    fig.savefig(args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output',
                        required=False,
                        default='-',
                        type=argparse.FileType(mode='w'))
    parser.add_argument('-v', '--verbose', action='store_true')
    main(parser.parse_args())
