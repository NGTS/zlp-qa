#!/usr/bin/env python
# -*- coding: utf-8 -*-

from astropy.io import fits
from qa_common.plotting import plt, subplots
from qa_common.qa_logging import get_logger
import numpy as np
import argparse

logger = get_logger(__file__)


def main(args):
    logger.info('Loading data from %s', args.filename)
    with fits.open(args.filename) as infile:
        flux = infile['flux'].data
        detflux = infile['casudet'].data

    logger.debug('Computing statistics')

    # Remember detflux is in magnitudes
    med_mags = np.median(detflux, axis=1)
    med_flux = np.median(flux, axis=1)

    undetrended_frms = flux.std(axis=1) / med_flux
    detrended_frms = detflux.std(axis=1)

    logger.info('Plotting to %s', args.output)
    with subplots(xlabels=['Magnitude'], ylabels=['Fractional rms']) as (fig, axes):
        axes[0].semilogy(med_mags, undetrended_frms, '.', alpha=0.3, label='Raw')
        axes[0].semilogy(med_mags, detrended_frms, '.', alpha=0.3, label='CASU')
        axes[0].set_xlim(10, 18)
        axes[0].set_ylim(1E-3, 1E-1)
        axes[0].legend(loc='best')
        axes[0].grid(True, which='both')

    fig.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output',
                        required=False,
                        default='-',
                        type=argparse.FileType(mode='w'))
    main(parser.parse_args())
