#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fitsio
import numpy as np
import os
import argparse
from collections import namedtuple
import sys
from qa_common.filter_objects import good_measurement_indices
from qa_common.plotting import plt
from qa_common import get_logger

logger = get_logger(__file__)

summary = namedtuple('Summary', ['mags', 'frms'])


def extract_flux_data(fname, hdu, zp=21.18, airmass_correct=False):
    with fitsio.FITS(fname) as infile:
        flux = infile[hdu].read()
        imagelist = infile['imagelist']
        airmass = imagelist['airmass'].read()
        exptime = imagelist['exposure'].read()

        ccdx = infile['ccdx'][:,:1].flatten()
        ccdy = infile['ccdy'][:,:1].flatten()

    logger.info('Normalising by exposure time')
    flux /= exptime

    av_flux = np.average(flux, axis=1)
    std_flux = np.std(flux, axis=1)

    before_size = av_flux.size

    ind = ((av_flux > 0) & (std_flux > 0) & (av_flux == av_flux) &
           (std_flux == std_flux))
    av_flux, std_flux = [data[ind] for data in [av_flux, std_flux]]

    logger.info("Rejecting %s objects", before_size - av_flux.size)

    mags = zp - 2.5 * np.log10(av_flux)

    return summary(mags.astype(float), (std_flux / av_flux).astype(float))


def plot_summary(s, colour, label='', ax=None):
    ax = ax if ax else plt.gca()

    ax.plot(s.mags, s.frms, ls='None', marker='.', color=colour, label=label)


def main(args):
    logger.info('Loading flux data from %s', args.filename)
    extracted = extract_flux_data(args.filename, hdu=args.hdu)

    fig, ax = plt.subplots(figsize=(11, 8))
    plot_summary(extracted, 'r', ax=ax)
    ax.set(xlabel='Kepler magnitude', ylabel='FRMS', yscale='log',
            title='{}:{}'.format(os.path.basename(args.filename), args.hdu),
            xlim=(5, 20), ylim=(1E-3, 10))
    ax.yaxis.set_major_formatter(plt.ScalarFormatter())
    ax.grid(True)
    fig.tight_layout()

    logger.info('Saving to %s', args.output)
    if args.output is not None:
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        help='Output image name')
    parser.add_argument('filename', help='File to analyse')
    parser.add_argument('-H', '--hdu', help='HDU to analyse', required=True)

    main(parser.parse_args())
